// 渲染 PDF 每页为 PNG，检查页数，并报告每页内容延伸到页面多低的位置。
// （排版检查，见 docs/REVIEW-CHECKLIST.md C 节。）
//
// 「到达位置」(reach) = 最后一行有内容的位置 / 页高，以百分比表示。它不是页面的使用面积：
// 页面底部孤零零一个页脚，就会让一张几乎空白的页面看起来是满的。用 --ignore-bottom 跳过页脚区域，
// 并且一定要看生成的 PNG。
//
// 用法：swift scripts/pdf_fill.swift <cv.pdf> <输出目录> [--pages=1,2] [--min-reach=85] [--ignore-bottom=0]
//   --pages=1,2         允许的页数，逗号分隔（默认 1,2）
//   --min-reach=85      最后一页内容的最低到达位置，百分比（默认 85）
//   --ignore-bottom=0   忽略每页底部的 N%，比如页脚（默认 0）
// 第三个位置参数（一个数字）仍然当作 --min-reach 使用。
// 退出码：0 = 通过，2 = 排版有问题，1 = 打不开 PDF，64 = 用法错误。
// 依赖：macOS（PDFKit / AppKit）

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
  print("用法: swift pdf_fill.swift <cv.pdf> <输出目录> [--pages=1,2] [--min-reach=85] [--ignore-bottom=0]")
  exit(64)
}
if positional.count > 2, let d = Double(positional[2]) { minReach = d }
let url = URL(fileURLWithPath: positional[0])
let outDir = positional[1]

guard let doc = PDFDocument(url: url) else { print("无法打开 PDF: \(positional[0])"); exit(1) }
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
  ), let ctx = NSGraphicsContext(bitmapImageRep: rep) else { print("渲染失败: 第 \(i + 1) 页"); exit(1) }

  NSGraphicsContext.saveGraphicsState()
  NSGraphicsContext.current = ctx
  ctx.cgContext.setFillColor(NSColor.white.cgColor)
  ctx.cgContext.fill(CGRect(x: 0, y: 0, width: w, height: h))
  ctx.cgContext.scaleBy(x: scale, y: scale)
  page.draw(with: .mediaBox, to: ctx.cgContext)
  NSGraphicsContext.restoreGraphicsState()

  // 从上往下找最后一个有内容的像素行，跳过被忽略的底部区域
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
  let ok = allowedPages.sorted().map(String.init).joined(separator: " 或 ")
  problems.append("页数是 \(doc.pageCount)，应为 \(ok)")
}
let lastReach = reaches.last ?? 0
if lastReach < minReach {
  problems.append(String(format: "最后一页的内容只到页面高度的 %.0f%%（最低 %.0f%%）。请补充有证据的内容，或精简并重新排版让页面填满（D-009）", lastReach, minReach))
}

if problems.isEmpty {
  print(String(format: "通过：%d 页，最后一页到达 %.0f%%", doc.pageCount, lastReach))
} else {
  for p in problems { print("⚠️ " + p) }
}
print("提示：到达位置是最后一处内容结束的地方，不是页面的使用面积。请同时看生成的 PNG。")
exit(problems.isEmpty ? 0 : 2)
