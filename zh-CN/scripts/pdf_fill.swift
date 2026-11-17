// 渲染 PDF 每页为 PNG，并报告每页内容填充率（排版检查，见 docs/REVIEW-CHECKLIST.md C 节）。
// 填充率 = 页面最后一行有内容的位置 / 页高。最后一页低于阈值时退出码为 2。
//
// 用法：swift scripts/pdf_fill.swift <cv.pdf> <输出目录> [最后一页最低填充率，默认 85]
// 依赖：macOS（PDFKit / AppKit）

import Foundation
import PDFKit
import AppKit

let args = CommandLine.arguments
guard args.count >= 3 else {
  print("用法: swift pdf_fill.swift <cv.pdf> <输出目录> [最低填充率 %]")
  exit(64)
}
let url = URL(fileURLWithPath: args[1])
let outDir = args[2]
let threshold = args.count > 3 ? (Double(args[3]) ?? 85) : 85

guard let doc = PDFDocument(url: url) else { print("无法打开 PDF: \(args[1])"); exit(1) }
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
  ), let ctx = NSGraphicsContext(bitmapImageRep: rep) else { print("渲染失败: 第 \(i + 1) 页"); exit(1) }

  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = ctx
  ctx.cgContext.setFillColor(NSColor.white.cgColor)
  ctx.cgContext.fill(CGRect(x: 0, y: 0, width: w, height: h))
  ctx.cgContext.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx.cgContext)
  NSGraphicsContext.restoreGraphicsState()

  // 从上往下找最后一个有内容的像素行
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
  print(String(format: "⚠️ 最后一页填充率 %.0f%% < %.0f%%：多出的内容太少，请精简内容或调排版（D-009）", lastFill, threshold))
  exit(2)
}
