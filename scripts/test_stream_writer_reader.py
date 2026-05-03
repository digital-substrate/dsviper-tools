from __future__ import annotations
from dsviper import *
import os

FILENAME = "/Volumes/DigitalSubstrate/dsm-samples/Re"
report, dsm_defs, defs = DSMBuilder.assemble(FILENAME).parse()

if report.has_error():
    for error in report.errors():
        print(error)

defs = dsm_defs.to_definitions()

swb = StreamWriterBlob()
sbw = StreamTokenBinaryWriter(swb.stream_raw_writing())
dsm_defs.write(sbw.stream_writing())
blob = swb.blob()
br = StreamReaderBlob(blob)
sbr = StreamTokenBinaryReader(br.stream_raw_reading())
d = DSMDefinitions.read(sbr.stream_reading())

swb = StreamWriterBlob()
sbw = StreamTokenBinaryWriter(swb.stream_raw_writing())
defs.const().write(sbw.stream_writing())
blob = swb.blob()
br = StreamReaderBlob(blob)
sbr = StreamTokenBinaryReader(br.stream_raw_reading())
d = Definitions.read(sbr.stream_reading())

FILE = os.path.expanduser("~/test.bin")
if os.path.exists(FILE):
    os.remove(FILE)

swf = StreamWriterFile(FILE)
sbw = StreamTokenBinaryWriter(swf.stream_raw_writing())
dsm_defs.write(sbw.stream_writing())
print(f'{swf.offset()=}')
swf.close()

srf = StreamReaderFile(FILE)
sbr = StreamTokenBinaryReader(srf.stream_raw_reading())
d = DSMDefinitions.read(sbr.stream_reading())
print(f'{srf.offset()=}')
srf.close()


swb = StreamWriterBlob()
sbw = StreamRawWriter(swb.stream_raw_writing())
defs.const().write(sbw.stream_writing())
blob = swb.blob()
br = StreamReaderBlob(blob)
sbr = StreamRawReader(br.stream_raw_reading())
d = Definitions.read(sbr.stream_reading())

