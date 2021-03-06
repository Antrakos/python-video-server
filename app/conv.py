#!/usr/bin/env python3

"""
reencodes the first video stream of a media file as mpeg1 video.
"""

import sys
import pyrana
import pyrana.errors
import pyrana.formats
from pyrana.video import PixelFormat
from pyrana.formats import MediaType


def process_file(srcname, dstname):
    sys.stdout.write("%s -> %s\n" % (srcname, dstname))

    with open(srcname, 'rb') as src, open(dstname, 'wb') as dst:
        dmx = pyrana.formats.Demuxer(src)
        sid = pyrana.formats.find_stream(dmx.streams,
                                         0,
                                         MediaType.AVMEDIA_TYPE_VIDEO)
        vdec = dmx.open_decoder(sid)
        params = {
            'bit_rate': 800000,
            'width': 352,
            'height': 288,
            'time_base': (1, 25),
            'pix_fmt': PixelFormat.AV_PIX_FMT_YUV420P
        }
        mux = pyrana.formats.Muxer(dst, name='ogv')
        venc = mux.open_encoder('libtheora', params)
        mux.write_header()

        num = 0
        while True:
            frame = vdec.decode(dmx.stream(sid))
            try:
                pkt = venc.encode(frame)
                mux.write_frame(pkt)
                sys.stdout.write("encoded: %05i\r" % num)
            except pyrana.errors.NeedFeedError:
                sys.stderr.write("skipped: %05i\n" % num)
            num += 1

        mux.write_frame(venc.flush())
        mux.write_trailer()

    # dst.writes(bytes(venc.flush()))
    sys.stdout.write("\n")


def _main(srcname, dstname):
    """the usual entry point."""
    pyrana.setup()

    try:
        process_file(srcname, dstname)
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        _main(sys.argv[1], sys.argv[2])
    else:
        sys.stderr.write("usage: %s videofile mpeg1file\n" % sys.argv[0])
        sys.exit(1)
