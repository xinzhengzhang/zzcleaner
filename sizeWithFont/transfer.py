import os
from sys import argv

def getfont(row):
	if row.find("constrainedToSize") == -1 and row.find("forWidth") == -1:
		row2 = row[row.find("sizeWithFont:"):][len("sizeWithFont:"):]
		font = ""
		left = 0
		list = []
		for i in row2:
			if i == "[":
				left += 1
				list.append(i)
			elif i == "]" and left <= 1:
				if left == 1:
					list.append(i)
				left -= 1
				break
			else :list.append(i)
		return "".join(list)
	elif row.find("forWidth") != -1:
		row2 = row[row.find("sizeWithFont:"):][len("sizeWithFont:"):]
		r = row2.find("forWidth")
		return row2[:r]
	else:
		row2 = row[row.find("sizeWithFont:"):][len("sizeWithFont:"):]
		r = row2.find("constrainedToSize")
		return row2[:r]

def getsize(row):
	if row.find("forWidth") != -1:
		row2 = row[row.find("forWidth"):][len("forWidth"):]
		r = row2.find("lineBreakMode")
		return "CGSizeMake("+row2[1:r]+", 500)"
	else:
		l = row.find("constrainedToSize:")
		r = row.find("lineBreakMode")
		return row[l:r][len("constrainedToSize:"):]

def getbreakmode(row):
	l = row.find("lineBreakMode:")
	list = []
	for i in row[l:][len("lineBreakMode:"):]:
		if i == "]":
			break
		list.append(i)
	return "".join(list)

def getprefix(row):
	r = row.find("=")
	return row[:r+1]

def getsuffix(row):
	r = row.find("=")
	list = []
	start = False
	suffix = False
	left = 0
	for i in row[r:]:
		if suffix == True:
			list.append(i)
		if i == "[":
			left += 1
			start = True
		if i == "]":
			left -= 1
		if left == 0 and start == True:
			suffix = True
	return "".join(list)

def getivar(row):
	l = row.find("=")
	r = row.find("sizeWithFont")
	l2 = row[l:r].find("[")
	return row[l+l2+1:r]

def getpennding(row):
	list = []
	for i in row:
		if i == "\t" or i == " ":
			list.append(i)
	return "".join(list)

def createNewApi(pend, prefix, ivar, font, size, breakmode,suffix,varprefix):
	if size:
	 	return createBoundApi(pend, prefix, ivar, font, size, breakmode,suffix,varprefix)
	else:
		return createFontApi(pend,prefix,ivar,font,suffix,varprefix)
	
def createBoundApi(pend, prefix, ivar, font, size, breakmode,suffix,varprefix):
	if len(breakmode) == 0:
		breakmode = "NSLineBreakByWordWrapping"
	return pend+"NSMutableParagraphStyle * paragraphStyle"+varprefix+" = [[NSMutableParagraphStyle alloc] init];\n"+pend+"paragraphStyle"+varprefix+".lineBreakMode = "+breakmode+";\n"+pend+"paragraphStyle"+varprefix+".alignment = NSTextAlignmentLeft;\n\n"+pend+"NSDictionary * attributes"+varprefix+" = @{NSFontAttributeName : "+font+","+"NSParagraphStyleAttributeName : paragraphStyle"+varprefix+"};\n"+pend+prefix+"["+ivar+" boundingRectWithSize:"+size+" options:NSStringDrawingUsesFontLeading|NSStringDrawingUsesLineFragmentOrigin attributes:attributes"+varprefix+" context:nil].size"+suffix+"\n"

def createFontApi(pend,prefix, ivar, font,suffix,varprefix):
	return pend+prefix+"["+ivar+"sizeWithAttributes:@{NSFontAttributeName : "+font+"}]"+suffix+"\n"

def createApi(row,varprefix):
	print "row:\n", row
	suffix = getsuffix(row)
	row = row[:-len(suffix)]
	dealed = createNewApi(getpennding(row) ,getprefix(row), getivar(row), getfont(row), getsize(row), getbreakmode(row),suffix,varprefix)
	print "dealed:\n", dealed
	print "\n\n\nprint Y to confirm\n"
	import sys
	line = sys.stdin.readline()
	if line.strip() == "y":
		return dealed
	return None

def transfer(path):
	fd = open(path,"r")
	list = fd.readlines()
	fd.close()
	l = -1
	r = -1
	row = []
	for i in xrange(0,len(list)):
		if list[i].find("sizeWithFont") != -1	:
			l = i
		if l != -1:
			for j in list[i]:
				if j == ";":
					r = i
					row.append((l,r))
					l = -1
					r = -1

	l = 0
	dealedList = []
	if len(row) == 0:
		return
	else:
		print "transfer:", path

	for i in row:
		dealedList += (list[l:i[0]])
		t = list[i[0]:i[1]+1]
		dealed = createApi("".join(map(lambda x: x.strip(),t)), str(row.index(i)))
		if not dealed:
			assert "unknow error"
		dealedList += ([dealed])
		l = i[1]+1

	if l != len(list):
		dealedList += list[l:len(list)]
	fd = open(path,"w")
	fd.write("".join(dealedList))
	fd.close()

if __name__ == "__main__":
	assert len(argv) > 1,"Syntax: python transfer.py {rootpath}"
	for root, dirs, files in os.walk(argv[1]):
	    path = root.split('/')
	    print (len(path) - 1) *'---' , os.path.basename(root)       
	    for file in files:
			if file[-2:] == ".h" or file[-2:] == ".m":
				print len(path)*'---', file
				absroute = root+"/"+file
				transfer(absroute)
