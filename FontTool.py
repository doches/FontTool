#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

parser = OptionParser(usage="FontTool is a utility for creating bitmap fonts from TrueType font files.\n\nExample: `python FontTool.py -f arial` produces arial.font (font info) and arial.png (texture) from arial.ttf (which must be in the cwd).\n\npython %prog [options]")
parser.add_option("-f","--font",dest="font",help="(REQUIRED) Name of the font to load (looks for <font>.ttf in the working directory)")
parser.add_option("-s","--size",dest="size",type="int",help="Desired font size (in points). Defaults to 64.",default=64)
parser.add_option("--surface",dest="surface_size",help="Size of the surface into which to render, of the form WIDTHxHEIGHT). Defaults to 512x512.",default="512x512")
parser.add_option("-c","--color",dest="color",help="Color to render, of the form RRR,GGG,BBB. Defaults to 255,255,255.",default="255,255,255")
parser.add_option("--chars",dest="characters",help="List of characters to include. Defaults to a reasonable list of mixed case alphanumerics and punctuation.",default="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.:!?@#$%^&*()[]\"\'-/<>{}+;")
parser.add_option("--plist",action="store_true",dest="plist",default=False,help="Flag indicating that we want the font information in Apple plist format (for loading with NSDictionary).")
parser.add_option("--no-aa",action="store_false",dest="antialias",default=True,help="Disable anti-aliasing")

(options,parser) = parser.parse_args()

import pygame
from pygame.locals import *

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("FontTool")
pygame.init()

font = options.font
fontname = font +".ttf"
fontsize = options.size
surfsize = options.surface_size.split("x")
surfsize = (int(surfsize[0]),int(surfsize[1]))
color = options.color.split(",")
color = (int(color[0]),int(color[1]),int(color[2]))
chars = options.characters
image_filename = font+"-"+str(fontsize)+".png"
output = "font"
if options.plist:
	output = "plist"
text_filename = font+"-"+str(fontsize)+"."+output
antialias = options.antialias

# plist XML needs (at least) these characters escaped...
escapes = {"&":"&amp;","<":"&lt;",">":"&gt;","'":"&apos;","\"":"&quot;"}

surf = pygame.surface.Surface(surfsize,SRCALPHA)
font = pygame.font.Font(fontname,fontsize)

spacing = 0
x = spacing/2
y = surfsize[1]
linemax = 0
fout = open(text_filename,"w")
if output == "plist":
	fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
	fout.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
	fout.write("<plist version=\"1.0\">\n")
	fout.write("<dict>\n")
for c in chars:
	try:
		charsurf = font.render(c,antialias,color)
		charsize = charsurf.get_size()
		charsize = (charsize[0],charsize[1])
		if charsize[1] > linemax:
			linemax = charsize[1]
		if x + charsize[0] > surfsize[0]:
			x = spacing/2
			y -= linemax+spacing
			linemax = 0
		surf.blit(charsurf,(x,y-charsize[1]))
		if output == "plist":
			if c in escapes:
				c = escapes[c]
			fout.write("\t<key>" + c + "</key>\n")
			fout.write("\t<array>\n")
			for v in [x,surfsize[1]-y,charsize[0],charsize[1]]:
				fout.write("\t\t<integer>"+str(v)+"</integer>\n")
			fout.write("\t</array>\n")
		elif output == "font":
			fout.write(c + "\t" + str(x) + "\t" + str(surfsize[1]-y) + "\t" + str(charsize[0]) + "\t" + str(charsize[1]) + "\n")
		x += charsize[0]+spacing
	except pygame.error:
		print c

pygame.image.save(surf,image_filename)
if output == "plist":
	fout.write("</dict>\n</plist>\n")
fout.close
