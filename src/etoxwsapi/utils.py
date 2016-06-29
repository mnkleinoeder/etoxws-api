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

    def __init__(self, fname = None):
        self.sdfrecs = []
        self.linesep = b'\n'
        if fname:
            self.parse(fname)

    def __len__(self):
        return len(self.sdfrecs)

    def __getitem__(self, i):
        return self.sdfrecs[i]

    def __iter__(self):
        return iter(self.sdfrecs)

    def split(self, size):
        i = 0
        parts = []

        run = True
        while( run ):
            (m,n) = (size*i, size *(i+1))
            if n >= self.__len__():
                n = self.__len__()
                run = False
            #print m, n
            part = SDFFile()
            part.linesep = self.linesep
            part.sdfrecs = self.sdfrecs[ m:n ]
            parts.append(part)
            i += 1
        return parts

    def _parse(self, fp):
        ret = True
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
            ret = False
        self.sdfrecs.extend([ SDFRec(rec, self.linesep) for rec in recs])
        return ret

    def parse(self, fobj):
        if type(fobj) in types.StringTypes:
            with open(fobj, 'rb') as fp:
                if not self._parse(fp):
                    raise Exception("File is not a MOL/SDF file: '%s'"%(fobj))
        elif hasattr(fobj, 'seek'):
            if not self._parse(fobj):
                raise Exception("File object does not contain MOL/SDF data")
        else:
            raise Exception("arg cannot be parsed.")

    def to_string(self, ctab_only = False):
        outbuf = StringIO()
        self._write(outbuf, "".join( [ rec.to_string(ctab_only) for rec in self.sdfrecs] ))
        #outbuf.write("".join( [ rec.to_string().rstrip() for rec in self.sdfrecs] ))
        return outbuf.getvalue()

    def write(self, fname):
        with open(fname, 'w') as fp:
            fp.write( self.to_string() )

if __name__ == '__main__':
    f = SDFFile('/home/thomas/w45/git/etoxws-api/src/client/testdata/nci2000.sdf')
    assert(len(f) == 2000)
    parts = f.split(666)
    assert(len(parts) == 4)
    assert(len(parts[3]) == 2)
    print len(f), len(parts)
    with open('/home/thomas/w45/git/etoxws-api/src/client/testdata/nci2000.sdf', 'rb') as fp:
        sio = StringIO(fp.read())
        f = SDFFile()
        f.parse(sio)
        print len(f)
    #f[0].add_prop('M_BLA', "blubsi")
    #sys.stdout.write("'%s'"%(parts[3].to_string(True)))
    #parts[3].write('/tmp/t.sdf')