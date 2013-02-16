#!/usr/bin/env python
# coding=UTF8
import os
import sys
from optparse import OptionParser

parser = OptionParser(usage="FontTool is a utility for creating bitmap fonts from TrueType font files.\n\nExample: `python FontTool.py -f arial` produces arial.font (font info) and arial.png (texture) from arial.ttf (which must be in the cwd).\n\npython %prog [options]")
parser.add_option("-f","--font",dest="font",help="(REQUIRED) Name of the font to load (looks for <font>.ttf in the working directory)")
parser.add_option("-s","--size",dest="size",type="int",help="Desired font size (in points). Defaults to 64.",default=64)
parser.add_option("--surface",dest="surface_size",help="Size of the surface into which to render, of the form WIDTHxHEIGHT). Defaults to 512x512.",default="512x512")
parser.add_option("-c","--color",dest="color",help="Color to render, of the form RRR,GGG,BBB. Defaults to 255,255,255.",default="255,255,255")
parser.add_option("--chars",dest="characters",help="List of characters to include. Defaults to a reasonable list of mixed case alphanumerics and punctuation.",default=unicode("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,.:!?@#$^&*()[]\"\'-/<>{}+;=~\\_","UTF8","strict"))
parser.add_option("-x","--extra",dest="extra_characters",help="List of extra characters to include." ,default=unicode("","UTF8","strict"))
parser.add_option("--plist",action="store_true",dest="plist",default=False,help="Flag indicating that we want the font information in Apple plist format (for loading with NSDictionary).")
parser.add_option("-u","--unicode",action="store_true",dest="unicode",default=False,help="Include bonus unicode characters.")
parser.add_option("--no-aa",action="store_false",dest="antialias",default=True,help="Disable anti-aliasing")
parser.add_option("-o", "--output",dest="output",default="./",help="Directory into which to save files. Defaults to current directory.")
parser.add_option("--headless",action="store_true",dest="headless",help="Close and terminate process after creating font, without displaying the result.",default=False)
parser.add_option("-S","--spacing",dest="spacing",type="int",help="How many pixels of whitespace to pad around each character",default=1)

(options,parser) = parser.parse_args()

import pygame
from pygame.locals import *

surfsize = options.surface_size.split("x")
surfsize = (int(surfsize[0]),int(surfsize[1]))
screensize = surfsize#(1024,768)
screen = pygame.display.set_mode(screensize)
pygame.display.set_caption("FontTool")
pygame.init()

# plist XML needs (at least) these characters escaped...
escapes = {"&":"&amp;","<":"&lt;",">":"&gt;","'":"&apos;","\"":"&quot;"}

surf = pygame.surface.Surface(surfsize,SRCALPHA)

def render(do_save):
	fontname = options.font +".ttf"
	fontsize = options.size
	surf.fill((0, 0, 0, 0))

	print "font: " + fontname
	print "size: " + str(fontsize)
	font = pygame.font.Font(fontname,fontsize)
	color = options.color.split(",")
	color = (int(color[0]),int(color[1]),int(color[2]))
	chars = options.characters + options.extra_characters
	if options.unicode:
	  chars = chars + unicode("%éüùú£¢¡¿àáñöóòïíèáéíóúüñ","UTF8")
	image_filename = options.font+"-"+str(fontsize)+".png"
	output = "font"
	if options.plist:
		output = "plist"
	text_filename = options.font+"-"+str(fontsize)+"."+output
	antialias = options.antialias
	spacing = options.spacing
	x = 0
	y = surfsize[1]
	linemax = 0
	if do_save:
		fout = open(os.path.join(options.output,os.path.basename(text_filename)),"w")
		if output == "plist":
			fout.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
			fout.write("<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">\n")
			fout.write("<plist version=\"1.0\">\n")
			fout.write("<dict>\n")
	for c in chars:
		try:
			charsurf = font.render(c,antialias,color)
			charsize = charsurf.get_size()
			charsize = (charsize[0]+spacing,charsize[1]+spacing)
			if charsize[1] > linemax:
				linemax = charsize[1]
			if x + charsize[0] > surfsize[0]:
				x = 0
				y -= linemax
				linemax = 0
			surf.blit(charsurf,(x+spacing/2,y-charsize[1]+spacing/2))
			if do_save:
				if output == "plist":
					if c in escapes:
						c = escapes[c]
					fout.write("\t<key>" + c.encode("utf-8") + "</key>\n")
					fout.write("\t<array>\n")
					for v in [x,surfsize[1]-y,charsize[0],charsize[1]]:
						fout.write("\t\t<integer>"+str(v)+"</integer>\n")
					fout.write("\t</array>\n")
				elif output == "font":
					fout.write(c + "\t" + str(x) + "\t" + str(surfsize[1]-y) + "\t" + str(charsize[0]) + "\t" + str(charsize[1]) + "\n")
			x += charsize[0]
		except pygame.error:
			print c

	if do_save:
		pygame.image.save(surf,os.path.join(options.output,os.path.basename(image_filename)))
		if output == "plist":
			fout.write("</dict>\n</plist>\n")
		fout.close

render(options.headless)

if not options.headless:
	alive = True
	while alive:
		for event in pygame.event.get():
			if event.type == QUIT:
				alive = False
			if event.type == KEYDOWN:
				if event.key == K_RETURN or event.key == K_RETURN:
					render(True)
					alive = False
				if event.key == K_ESCAPE:
					alive = False
				if event.key == K_DOWN:
					options.size = options.size - 1
					render(False)
				if event.key == K_UP:
					options.size = options.size + 1
					render(False)
		screen.fill((32, 32, 32), None, 0)
		ypos = 0
		if screensize[1] < surfsize[1]:
			ypos = -(surfsize[1] - screensize[1])
		screen.blit(surf, (0, ypos), None, 0)
		pygame.display.flip()
