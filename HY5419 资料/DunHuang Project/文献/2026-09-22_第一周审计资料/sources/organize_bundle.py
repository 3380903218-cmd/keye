"""Organize this collection only; assemble PDFs without recompressing source JPEGs."""
from pathlib import Path
import json, struct, hashlib, csv
from embedded_scan_storage import read_scan_bytes

B = Path(__file__).resolve().parents[1]
F = B/'full-text'
renames = {}
def move(p, dest):
    if p.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        p.rename(dest)
        renames[str(p.relative_to(B))] = str(dest.relative_to(B))

for p in list(F.glob('*_scan_*.jpg')):
    move(p, B/'sources/scan-images'/p.name)
for p in list(F.glob('*manifest.json')) + list(F.glob('*volume.html')) + list(F.glob('*目录.html')) + list(F.glob('*metadata.html')):
    move(p, B/'sources/metadata'/p.name)
for p in [F/'S08_Pelliot_1908_Persee.html', B/'extracted/S08_Pelliot_1908_Persee.txt']:
    move(p, B/'sources/metadata'/p.name)
for p in [F/'S16_INHA_Pelliot_collection_history.html', B/'extracted/S16_INHA_Pelliot_collection_history.txt']:
    move(p, B/'sources/failed_responses'/p.name)
for ext, folder in [('pdf',F),('txt',B/'extracted')]:
    move(folder/('S11_NLC_2005_敦煌文献数字化.'+ext), folder/('S11_NLC_敦煌文献数字化.'+ext))
log = B/'sources/整理路径映射.json'
old = json.loads(log.read_text()) if log.exists() else {}
old.update(renames)
log.write_text(json.dumps(old,ensure_ascii=False,indent=2))

def jpeg_size(data):
    assert data[:2] == b'\xff\xd8'
    i = 2
    while i < len(data):
        assert data[i] == 255
        while data[i] == 255: i += 1
        marker = data[i]; i += 1
        if marker in [0xd8,0xd9] or 0xd0 <= marker <= 0xd7: continue
        size = int.from_bytes(data[i:i+2],'big')
        if marker in [0xc0,0xc1,0xc2]:
            bits,h,w,c = struct.unpack('>BHHB',data[i+2:i+8])
            assert bits == 8 and c in [1,3]
            return w,h,c
        i += size
    raise ValueError('JPEG SOF not found')

def make_pdf(paths, dest):
    objects = [b'',b'']; kids=[]
    def add(obj):
        objects.append(obj); return len(objects)
    for p in paths:
        data=read_scan_bytes(str(p.relative_to(B))); w,h,c=jpeg_size(data)
        pw,ph = w*842/max(w,h), h*842/max(w,h)
        img=add(('<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /%s /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n'%(w,h,'DeviceRGB' if c==3 else 'DeviceGray',len(data))).encode()+data+b'\nendstream')
        content=('q %.5f 0 0 %.5f 0 0 cm /Im0 Do Q'%(pw,ph)).encode()
        stream=add(('<< /Length %d >>\nstream\n'%len(content)).encode()+content+b'\nendstream')
        page=add(('<< /Type /Page /Parent 2 0 R /MediaBox [0 0 %.5f %.5f] /Resources << /XObject << /Im0 %d 0 R >> >> /Contents %d 0 R >>'%(pw,ph,img,stream)).encode())
        kids.append(page)
    objects[0]=b'<< /Type /Catalog /Pages 2 0 R >>'
    objects[1]=('<< /Type /Pages /Count %d /Kids [%s] >>'%(len(kids),' '.join('%d 0 R'%k for k in kids))).encode()
    out=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
    for n,obj in enumerate(objects,1):
        offsets.append(len(out)); out+=('%d 0 obj\n'%n).encode()+obj+b'\nendobj\n'
    pos=len(out);out+=('xref\n0 %d\n0000000000 65535 f \n'%len(offsets)).encode()
    for off in offsets[1:]:out+=('%010d 00000 n \n'%off).encode()
    out+=('trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n'%(len(offsets),pos)).encode()
    dest.write_bytes(out)
    return {'file':str(dest.relative_to(B)), 'page_count':len(paths),'sha256':hashlib.sha256(out).hexdigest(),'method':'Original JPEG bytes embedded; no OCR layer; no crop or recompression','inputs':[str(p.relative_to(B)) for p in paths]}

I=B/'sources/scan-images'
s07=[(311,823),(312,824),(313,825),(317,829),(318,830),(412,916)]
records=[make_pdf([I/('S07_scan_%04d.jpg'%n) for n,p in s07],F/'S07_Serindia_审计关键页_823-825_829-830_916.pdf'),make_pdf([I/('S22_scan_%04d.jpg'%n) for n in range(1,29)],F/'S22_Pelliot_1910_Trois_ans_完整扫描.pdf')]
(B/'sources/PDF合成记录.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
with (B/'扫描页码对照.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['SourceID','本地PDF页','印刷页或内容','原扫描文件','核对状态'])
    for i,(n,p) in enumerate(s07,1):w.writerow(['S07',i,p,'sources/scan-images/S07_scan_%04d.jpg'%n,'已目视核对页码及相关段落'])
    for n,label in [(5,'题名页：1909-12-10演讲；1910年出版'),(19,'13'),(20,'14'),(21,'15')]:w.writerow(['S22',n,label,'sources/scan-images/S22_scan_%04d.jpg'%n,'已目视核对；其余扫描保留原序未逐页精读'])
print(json.dumps(records,ensure_ascii=False,indent=2))
