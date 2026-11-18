// Renders each PDF page to a PNG, checks the page count, and reports how far down each page the content reaches.
// (Layout check; see section C of docs/REVIEW-CHECKLIST.md.)
//
// "Reach" = where the last row with content ends, as a percentage of the page height. It is NOT how much
// of the page is used: a lone footer near the bottom makes a nearly empty page look full. Use --ignore-bottom
// to skip a footer zone, and always look at the PNGs too.
//
// Usage: swift scripts/pdf_fill.swift <cv.pdf> <output-dir> [--pages=1,2] [--min-reach=85] [--ignore-bottom=0]
//   --pages=1,2         allowed page counts, comma-separated (default 1,2)
//   --min-reach=85      minimum reach of the LAST page, in percent (default 85)
//   --ignore-bottom=0   ignore the bottom N percent of every page, e.g. a footer (default 0)
// A third positional number is still accepted as --min-reach.
// Exit codes: 0 = OK, 2 = layout problem, 1 = cannot open the PDF, 64 = bad usage.
// Requires: macOS (PDFKit / AppKit)

import Foundation
import PDFKit
import AppKit

var allowedPages: Set<Int> = [1, 2]
var minReach = 85.0
var ignoreBottom = 0.0
var positional: [String] = []
for a in CommandLine.arguments.dropFirst() {
  if a.hasPrefix("--pages=") {
    let v = a.dropFirst("--pages=".count).split(separator: ",").compactMap { Int($0) }
    if !v.isEmpty { allowedPages = Set(v) }
  } else if a.hasPrefix("--min-reach=") {
    if let d = Double(a.dropFirst("--min-reach=".count)) { minReach = d }
  } else if a.hasPrefix("--ignore-bottom=") {
    if let d = Double(a.dropFirst("--ignore-bottom=".count)) { ignoreBottom = d }
  } else {
    positional.append(a)
  }
}
guard positional.count >= 2 else {
  print("Usage: swift pdf_fill.swift <cv.pdf> <output-dir> [--pages=1,2] [--min-reach=85] [--ignore-bottom=0]")
  exit(64)
}
if positional.count > 2, let d = Double(positional[2]) { minReach = d }
let url = URL(fileURLWithPath: positional[0])
let outDir = positional[1]

guard let doc = PDFDocument(url: url) else { print("Cannot open PDF: \(positional[0])"); exit(1) }
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

print("pages:", doc.pageCount)
var reaches: [Double] = []

for i in 0..<doc.pageCount {
  guard let page = doc.page(at: i) else { continue }
  let b = page.bounds(for: .mediaBox)
  let scale: CGFloat = 1.5
  let w = Int(b.width * scale), h = Int(b.height * scale)
  guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8,
    samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
    colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0
  ), let ctx = NSGraphicsContext(bitmapImageRep: rep) else { print("Render failed: page \(i + 1)"); exit(1) }

  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = ctx
  ctx.cgContext.setFillColor(NSColor.white.cgColor)
  ctx.cgContext.fill(CGRect(x: 0, y: 0, width: w, height: h))
  ctx.cgContext.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx.cgContext)
  NSGraphicsContext.restoreGraphicsState()

  // Find the last pixel row that has content, skipping the ignored bottom zone
  let limit = Int(Double(h) * (100 - ignoreBottom) / 100)
  var last = 0
  for y in 0..<min(limit, h) {
    var dark = false
    for x in stride(from: 0, to: w, by: 3) {
      if let c = rep.colorAt(x: x, y: y), c.brightnessComponent < 0.85 { dark = true; break }
    }
    if dark { last = y }
  }
  let reach = Double(last) / Double(h) * 100
  reaches.append(reach)
  print(String(format: "page %d reach %.0f%%", i + 1, reach))

  if let png = rep.representation(using: .png, properties: [:]) {
    try? png.write(to: URL(fileURLWithPath: "\(outDir)/p\(i + 1).png"))
  }
}

var problems: [String] = []
if !allowedPages.contains(doc.pageCount) {
  let ok = allowedPages.sorted().map(String.init).joined(separator: " or ")
  problems.append("Page count is \(doc.pageCount); expected \(ok)")
}
let lastReach = reaches.last ?? 0
if lastReach < minReach {
  problems.append(String(format: "Content on the last page reaches only %.0f%% of the page height (minimum %.0f%%). Add real content, or trim and re-flow so the pages fill (D-009)", lastReach, minReach))
}

if problems.isEmpty {
  print(String(format: "OK: %d page(s), last page reaches %.0f%%", doc.pageCount, lastReach))
} else {
  for p in problems { print("⚠️ " + p) }
}
print("Note: reach is where the last content ends, not how much of the page is used. Look at the PNGs too.")
exit(problems.isEmpty ? 0 : 2)
