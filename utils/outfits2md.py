#!/usr/bin/python

from sys import argv
import xml.etree.ElementTree as ET


def main(args):
   names=['']*len(args)
   L=[dict() for a in args]
   done=dict()
   acc=[]

   for i in range(len(args)):
      T=ET.parse(args[i]).getroot()
      for t in T.iter():
         try:
            n=float(t.text)
            L[i][t.tag]=t.text
            if not done.has_key(t.tag):
               done[t.tag]=(n,n)
               acc.append(t.tag)
            else:
               (mi,ma)=done[t.tag]
               done[t.tag]=(min(mi,n),max(ma,n))
         except:
            pass

      if 'name' in T.attrib:
         names[i]=T.attrib['name']

      for e in T.findall("./general/shortname"):
         names[i]=e.text
         break

   Res=[[k]+[l[k] if k in l else '' for l in L] for k in acc]
   names=['']+names
   length=map(len,names)

   for r in Res:
      length=[max(n,len(s)) for (n,s) in zip(length,r)]

   mklin=lambda L:'| '+' | '.join(L)+' |'
   fmt=lambda (s,n):(n-len(s))*' '+s

   def emph(s,(mi,ma)):
      if s!='' and mi!=ma:
         if float(s)==mi:
            return "_"+s+"_"
         elif float(s)==ma:
            return "**"+s+"**"
      return s

   print mklin(map(fmt,zip(names,length)))
   print mklin(['-'*n for n in length])
   for r in Res:
      r=[r[0].replace("_"," ")]+[emph(k,done[r[0]]) for k in r[1:]]
      print mklin(map(fmt,zip(r,length)))

if '-h' in argv[1:] or '--help' in argv[1:] or len(argv)<2:
   print "usage:",argv[0],'<outfitname1.xml> ...'
else:
   main([f for f in argv[1:] if f.endswith(".xml")])

