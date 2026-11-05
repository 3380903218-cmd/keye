import Foundation
import PDFKit
import AppKit
let base=URL(fileURLWithPath:CommandLine.arguments[1])
var urls=try FileManager.default.contentsOfDirectory(at:base.appendingPathComponent("full-text"),includingPropertiesForKeys:nil).filter{$0.pathExtension=="pdf"}.sorted{$0.path<$1.path}
urls += [base.appendingPathComponent("../wang-yuanlu-the-first-curator-of-the-stein-collections-dunhuang-corpus.pdf"),base.appendingPathComponent("../Terzi_Whitfield_2024_Reconstructing_a_Medieval_Library_Dunhuang.pdf")]
var records:[[String:Any]]=[]
for url in urls {
 guard let doc=PDFDocument(url:url) else {fatalError("Cannot open \(url)")}
 var txt="";var count=0
 for i in 0..<doc.pageCount {guard let page=doc.page(at:i) else{fatalError("Page missing")};let s=page.string ?? "";count += s.count;txt += "\n===== PAGE \(i+1) =====\n"+s+"\n"}
 var name=url.deletingPathExtension().lastPathComponent
 if name.hasPrefix("wang-yuanlu") {name="S01_Doumy_2025_正式版"}
 if name.hasPrefix("Terzi_"){name="S03_Terzi_Whitfield_2024"}
 if !name.hasPrefix("S07_") && !name.hasPrefix("S22_"){try txt.write(to:base.appendingPathComponent("extracted/"+name+".txt"),atomically:true,encoding:.utf8)}
 records.append(["file":url.standardizedFileURL.path,"pages":doc.pageCount,"text_characters":count,"all_pages_parse":true])
 let pageNo=name.hasPrefix("S07_") ? 2 : name.hasPrefix("S22_") ? 18 : -1
 if pageNo >= 0,let page=doc.page(at:pageNo){let thumb=page.thumbnail(of:NSSize(width:1200,height:1600),for:.mediaBox);if let tiff=thumb.tiffRepresentation,let bitmap=NSBitmapImageRep(data:tiff),let png=bitmap.representation(using:.png,properties:[:]){try png.write(to:URL(fileURLWithPath:"/private/tmp/hy5419_planning_review/"+String(name.prefix(3))+"_assembled.png"))}}
}
let data=try JSONSerialization.data(withJSONObject:records,options:[.prettyPrinted,.sortedKeys])
try data.write(to:base.appendingPathComponent("sources/PDF解析校验.json"))
print(String(data:data,encoding:.utf8)!)
