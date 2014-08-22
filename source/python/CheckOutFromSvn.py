import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

def checkOut(projectName, svnLog, option, dest):
    dictProject = {'math'       :'http://svn.apache.org/repos/asf/commons/proper/math/trunk/',
                   'lang'       :'http://svn.apache.org/repos/asf/commons/proper/lang/trunk/',
                   'gson'       :'http://google-gson.googlecode.com/svn/trunk/',
                   'jfreechart' :'svn://svn.code.sf.net/p/jfreechart/code/trunk',
                   'collections':'http://svn.apache.org/repos/asf/commons/proper/collections/trunk/',
                   'dbcp'       :'http://svn.apache.org/repos/asf/commons/proper/dbcp/trunk/',
                   'httpclient' :'http://svn.apache.org/repos/asf/httpcomponents/httpclient/trunk/',
                   'jackrabbit' :'http://svn.apache.org/repos/asf/jackrabbit/trunk/',
                   'lucene'     :'http://svn.apache.org/repos/asf/lucene/dev/trunk/',
                   'ejbthree'   :'http://anonsvn.jboss.org/repos/jbossas/projects/ejb3/trunk/core/'}
    listOption = ["all", "testpair"]

    if (projectName not in dictProject) or (option not in listOption):
        print('Wrong project name or option: ' + projectName + ' ' + option)
        sys.exit(0)
      
    if not os.path.isfile(svnLog):
        print 'Invalid file: ' + svnLog
        sys.exit(0)

    destDir = dest
    if not re.search('/$', dest):
        destDir += '/'
    
    if os.path.isdir(destDir):
        print 'Destination directory already exists.'
    else:
        print 'Destination directory does not exist.'
        print 'This program makes the directory.'
        os.makedirs(destDir, 0700) # 0700 is the permission

    svnUrl = dictProject[projectName]
    root = ET.parse(svnLog).getroot()
    if option == 'all':
        numRev= 0
        for logentry in root.getiterator('logentry'):
            numRev += 1
            revision = int(logentry.get('revision'))
            checkout = 'svn checkout --revision ' + str(revision) + ' ' + svnUrl + ' ' + destDir + projectName + str(revision)
            subprocess.call(checkout, shell=True)
        print 'Checking out ' + str(numRev) + ' revisions is finished.'
    elif option == 'testpair':
        listCheckedOut = []
        shouldCheckOut = 0
        for logentry in root.getiterator('logentry'):
            revision = int(logentry.get('revision'))
            if shouldCheckOut == 1:
                shouldCheckOut = 0
                if not (revision in listCheckedOut):
                    listCheckedOut.append(revision)
                    checkout = 'svn checkout --revision ' + str(revision) + ' ' + svnUrl + ' ' + destDir + projectName + str(revision)
                    subprocess.call(checkout, shell=True)
            for path in logentry.getiterator('path'):
                # A, R, M, D: Added, Replaced, Modified, Deleted
                #if(((path.get('kind') == 'file') or (path.get('kind') == '')) and
                if((path.get('kind') == 'file') and
                   (path.get('action') != 'D') and
                   re.search('\\/test[s]{0,1}\\/.*\.[Jj]ava$', path.text)):
                   #re.search('Test[^/]*\.[Jj]ava$', path.text)):
                    shouldCheckOut = 1
                    if not (revision in listCheckedOut):
                        listCheckedOut.append(revision)
                        checkout = 'svn checkout --revision ' + str(revision) + ' ' + svnUrl + ' ' + destDir + projectName + str(revision)
                        subprocess.call(checkout, shell=True)
                    break
    print('Checking out ' + str(len(listCheckedOut)) + ' revisions is finished.')

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('python ./CheckOutFromSvn.py [arg1] [arg2] [arg3] [arg4]')
        print('[arg1] input  - project name')
        print('       (math, lang, collections, gson, jfreechart, ...)')
        print('[arg2] input  - svn log file')
        print('[arg3] input  - checkout option (all, testpair)')
        print('[arg4] output - destination directory')
        sys.exit(0)

    checkOut(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])

