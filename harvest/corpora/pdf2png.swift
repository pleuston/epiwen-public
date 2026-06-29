import Foundation
import PDFKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

// usage: swift pdf2png.swift <pdf> <outdir> [maxPages]  → writes <outdir>/<base>_<n>.png at 2x
let a = CommandLine.arguments
guard a.count >= 3, let doc = PDFDocument(url: URL(fileURLWithPath: a[1])) else {
    FileHandle.standardError.write("ERR open\n".data(using: .utf8)!); exit(1)
}
let outdir = a[2]
let maxP = a.count > 3 ? (Int(a[3]) ?? doc.pageCount) : doc.pageCount
let base = URL(fileURLWithPath: a[1]).deletingPathExtension().lastPathComponent
try? FileManager.default.createDirectory(atPath: outdir, withIntermediateDirectories: true)
let scale: CGFloat = 2.0
var written = 0
for i in 0..<min(maxP, doc.pageCount) {
    guard let page = doc.page(at: i) else { continue }
    let r = page.bounds(for: .mediaBox)
    let w = Int(r.width * scale), h = Int(r.height * scale)
    guard w > 0, h > 0, let ctx = CGContext(data: nil, width: w, height: h, bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpaceCreateDeviceRGB(), bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue) else { continue }
    ctx.setFillColor(CGColor(red: 1, green: 1, blue: 1, alpha: 1)); ctx.fill(CGRect(x: 0, y: 0, width: w, height: h))
    ctx.scaleBy(x: scale, y: scale); page.draw(with: .mediaBox, to: ctx)
    guard let cg = ctx.makeImage() else { continue }
    let p = String(format: "%@/%@_%03d.png", outdir, base, i + 1)
    guard let dest = CGImageDestinationCreateWithURL(URL(fileURLWithPath: p) as CFURL, UTType.png.identifier as CFString, 1, nil) else { continue }
    CGImageDestinationAddImage(dest, cg, nil); CGImageDestinationFinalize(dest); written += 1
}
print("wrote \(written) png(s) to \(outdir)")
