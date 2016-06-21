#from cStringIO import StringIO
from collections import OrderedDict

from StringIO import StringIO
import re
import sys
import logging

logger = logging.getLogger('SDF utils')

class WriteMixin():
    def _write(self, fp, item):
        fp.write("%s%s"%(item, b'%s'%(self.linesep)))

class SDFRec(object, WriteMixin):
    re_prop = re.compile('>.*<(.*)>.*')
    def __init__(self, rec, linesep):
        self.linesep = linesep
        self.rec = rec
        self.ctab = ""
        self.proptab = ""
        self.props = OrderedDict()
        self._parse()
        #print "'%s'"%(self.rec)

    def add_prop(self, propname, propvalue):
        # TODO: handle array props
        # if isinstance(propvalue, types.listType):
        logger.debug('Adding prop: %s -> %s'%(propname, propvalue))
        self.props[propname] = propvalue

    def to_string(self, ctab_only = False):
        outbuf = StringIO()
        self._write(outbuf, self.ctab)
        #print >>outbuf, self.proptab,
        if not ctab_only:
            for k,v in self.props.iteritems():
                self._write(outbuf, '>  <%s>'%(k))
                self._write(outbuf, v)
                if v:
                    self._write(outbuf, "")
        self._write(outbuf, '$$$$')
        return outbuf.getvalue()

    def _cat_line(self, line):
        l = line.rstrip()
        #print (l  + self.linesep),
        return l + self.linesep

    def _parse(self):
        is_ctab = True
        propname = None
        propentry = ""
        for line in StringIO(self.rec):
            if is_ctab:
                self.ctab += self._cat_line(line)
            if line[0] == 'M' and line.startswith("M  END"):
                    is_ctab = False
                    continue
            if is_ctab:
                continue
            self.proptab += self._cat_line(line)
            m = self.re_prop.match(line)
            if m:
                if propname:
                    self.add_prop(propname, propentry.rstrip())
                propname = m.group(1)
                propentry = ""
            else:
                propentry += self._cat_line(line)
        if propname:
            self.add_prop(propname, propentry.rstrip())
        self.ctab = self.ctab.rstrip()
        self.proptab = self.proptab.rstrip()

class SDFFile(object, WriteMixin):
    def __init__(self, fname):
        self.sdfrecs = []
        self.linesep = b'\n'
        self.parse(fname)

    def __len__(self):
        return len(self.sdfrecs)

    def __getitem__(self, i):
        return self.sdfrecs[i]

    def __iter__(self):
        return iter(self.sdfrecs)

    def parse(self, fname):
        with open(fname, 'rb') as fp:
            chunk = fp.read(1024)
            # handling mixed line feeds
            if chunk.count('\r\n') >= chunk.count('\n'):
                #print "is windows"
                self.linesep = b'\r\n'
            fp.seek(0)

            content = fp.read() 
            if '$$$$' in content:
                recs = content.split('$$$$')[:-1]
            elif 'M  END' in content:
                recs = [ content ]
            else:
                raise Exception("File is not a MOL/SDF file: '%s'"%(fname))
            self.sdfrecs.extend([ SDFRec(rec, self.linesep) for rec in recs])

    def to_string(self, ctab_only = False):
        outbuf = StringIO()
        self._write(outbuf, "".join( [ rec.to_string(ctab_only).rstrip() for rec in self.sdfrecs] ))
        #outbuf.write("".join( [ rec.to_string().rstrip() for rec in self.sdfrecs] ))
        return outbuf.getvalue()

    def write(self, fname):
        with open(fname, 'w') as fp:
            fp.write( self.to_string() )

if __name__ == '__main__':
    f = SDFFile('client/testdata/tiny.sdf')
    f[0].add_prop('M_BLA', "blubsi")
    sys.stdout.write("'%s'"%(f[0].to_string(True)))
    f.write('/home/thomas/w45/git/etoxws-api/src/client/testdata/t.sdf')
