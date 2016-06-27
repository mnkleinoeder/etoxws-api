#from cStringIO import StringIO
from collections import OrderedDict

from StringIO import StringIO
import re
import sys
import logging
import types

logger = logging.getLogger('SDF utils')

try:
    from rdkit import Chem
    def _check_rec(rec):
        # TODO: implement check for correct ctab using rdkit
        return True
except ImportError, e:
    def _check_rec(rec):
        return True

class WriteMixin():
    def _write(self, fp, item):
        fp.write("%s%s"%(item, b'%s'%(self.linesep)))

class SDFRec(object, WriteMixin):
    re_prop = re.compile('>.*<(.*)>.*')
    re_v3000 = re.compile('V3000')
    def __init__(self, rec, linesep):
        #print '->%s<-'%(rec)
        self.is_v3000 = False
        self.is_valid = True
        self.linesep = linesep
        self.rec = rec
        self.ctab = ""
        self.proptab = ""
        self.props = OrderedDict()

        self._parse()
        _check_rec(self.to_string(ctab_only=True))
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
                if type(v) in types.StringTypes and len(v) == 0:
                    # if the prop value is an emtpy string we don't need an extra CR
                    pass
                else:
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
        for lno, line in enumerate(StringIO(self.rec)):
            if is_ctab:
                if lno == 3:
                    if self.re_v3000.search(line):
                        self.is_v3000 = True
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
        #print self.is_v3000

class SDFFile(object, WriteMixin):
    re_rec = re.compile('\$\$\$\$[\n\r]{0,1}') # sometimes the eof is missing

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
                recs = self.re_rec.split(content)[:-1]
            elif 'M  END' in content:
                recs = [ content ]
            else:
                raise Exception("File is not a MOL/SDF file: '%s'"%(fname))
            self.sdfrecs.extend([ SDFRec(rec, self.linesep) for rec in recs])

    def to_string(self, ctab_only = False):
        outbuf = StringIO()
        self._write(outbuf, "".join( [ rec.to_string(ctab_only) for rec in self.sdfrecs] ))
        #outbuf.write("".join( [ rec.to_string().rstrip() for rec in self.sdfrecs] ))
        return outbuf.getvalue()

    def write(self, fname):
        with open(fname, 'w') as fp:
            fp.write( self.to_string() )

if __name__ == '__main__':
    f = SDFFile('client/testdata/tine.sdf')
    print len(f)
#     f[0].add_prop('M_BLA', "blubsi")
#     sys.stdout.write("'%s'"%(f[0].to_string(True)))
    f.write('/tmp/t.sdf')
