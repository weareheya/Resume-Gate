// Renders each PDF page to a PNG and reports how full each page is (layout check; see section C of docs/REVIEW-CHECKLIST.md).
// Fill rate = position of the last row with content / page height. Exits with code 2 if the last page is below the threshold.
//
// Usage: swift scripts/pdf_fill.swift <cv.pdf> <output-dir> [min fill % for the last page, default 85]
// Requires: macOS (PDFKit / AppKit)

import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
  print("Usage: swift pdf_fill.swift <cv.pdf> <output-dir> [min fill %]")
  exit(64)
}
let url = URL(fileURLWithPath: args[1])
let outDir = args[2]
let threshold = args.count > 3 ? (Double(args[3]) ?? 85) : 85

guard let doc = PDFDocument(url: url) else { print("Cannot open PDF: \(args[1])"); exit(1) }
try? FileManager.default.createDirectory(atPath: outDir, withIntermediateDirectories: true)

print("pages:", doc.pageCount)
var lastFill = 0.0

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

  // Find the last pixel row that has content
  var last = 0
  for y in 0..<h {
    var dark = false
    for x in stride(from: 0, to: w, by: 3) {
      if let c = rep.colorAt(x: x, y: y), c.brightnessComponent < 0.85 { dark = true; break }
    }
    if dark { last = y }
  }
  lastFill = Double(last) / Double(h) * 100
  print(String(format: "page %d fill %.0f%%", i + 1, lastFill))

  if let png = rep.representation(using: .png, properties: [:]) {
    try? png.write(to: URL(fileURLWithPath: "\(outDir)/p\(i + 1).png"))
  }
}

if doc.pageCount > 1 && lastFill < threshold {
  print(String(format: "⚠️ Last page is only %.0f%% full (minimum %.0f%%): too little spills over. Trim content or adjust layout (D-009)", lastFill, threshold))
  exit(2)
}
