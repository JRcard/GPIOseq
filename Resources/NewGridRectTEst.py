# encoding: utf-8

import wx
from constants import *
from variables import *
from widgets import *


class Grid(wx.Panel):
    def __init__(self, parent, pos, size, zoom=1):
        wx.Panel.__init__(self, parent, pos=pos, size=(size[0]*zoom,size[1]))  ### !!! watch size avec scrollBar!!! ###
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        
        ### la scrollbar apparait mais ne fonctionne pas....
#        self.scroll = wx.ScrollBar(self, -1, pos=(TRACKNAME_POS[0],TRACKNAME_POS[1]+(TRACK_TOTAL*GRID_STEP)),
#                                   size=(GRID_SIZE[0],15), style=wx.SB_HORIZONTAL)
        self.preview = None
        self.rectangles = []
        self.isPreview = False
        self.isDrag = False
        self.dragID = 0
        self.dragX = 0
        self.dragY = 0
        self.pos = None
        self.zoom = zoom

#        self.Bind(wx.EVT_SCROLL, self.onScroll)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.onMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.onMouseLeftUp)
#        self.Bind(wx.EVT_RIGHT_DOWN, self.onMouseRightDown)
#        self.Bind(wx.EVT_RIGHT_UP,self.onMouseRightUp)
        self.Bind(wx.EVT_MOTION, self.onMotion)  
        
            
    def onMouseLeftDown(self,e):
        self.CaptureMouse()
        self.pos = self.clip(e.GetPositionTuple())
        #rectID = self.getRectID(self.pos)
        mx = self.pos[0]/self.zoom
        my = self.pos[1]
        for rec in self.rectangles:
            if rec.Contains(self.pos):
                self.dragID = self.rectangles.index(rec)
                self.isDrag = True
                self.dragX = mx - self.rectangles[rec].X
                self.dragY = my - self.rectangles[rec].Y

                
            elif not rec.Contains(self.pos):
                self.previewRect = Rectangle(mx,my,0,GRID_STEP)
                self.isPreview = True
                self.rectangles.append(self.previewRect)

            

            
    def onMotion(self,e):
        if self.HasCapture():
            self.pos = self.clip(e.GetPositionTuple())
            mx = self.pos[0]/self.zoom
            my = self.pos[1]
            if self.isPreview:
                self.previewRect.width = max(0,mx-self.previewRect.X)
                self.Refresh()
                
            elif self.isDrag:
                self.rectangles[self.dragID].X = mx - self.dragX
                self.rectangles[self.dragID].Y = my - self.dragY
                self.Refresh()
        

    def onMouseLeftUp(self,e):
        if self.HasCapture():
            self.ReleaseMouse()
            self.pos = self.clip(e.GetPositionTuple())
            if self.isPreview:
                self.isPreview = False
                self.Refresh()
                if self.previewRect.width <= 0:
                    print "rectangles remove from list: ", self.rectangles[-1]
                    self.rectangles.pop()
                    
                else:
                    print self.rectangles

            elif self.isDrag:
                self.isdrag = False
                print "release: ", self.rectangles[self.dragID]
                
            else:
                print "ERROR: go back to work!!"
                
                
    def onPaint(self,e):
        dc = wx.AutoBufferedPaintDC(self)
        
        # PANEL IN BACKGROUND #######      
        self.backGround(dc)
        
        # TIMELINE #####        
        self.timeLine(dc)
        
        # GRID #######   
        self.squares(dc) 
        
        for rec in self.rectangles:
            rec.draw(dc,self.zoom,"#000099", "#0000ff")
            
            if self.isPreview:
                self.preview = self.rectangles[-1].draw(dc,self.zoom,"#0000ff", "#000000")
                

######## fonctions generales  #########

    def backGround(self,dc):
        x, y = self.GetSize()        
        dc.SetBrush(wx.Brush("#000000"))
        dc.DrawRectangle(0,0, x,y)
        
    def timeLine(self,dc):
        dc.SetBrush(wx.Brush("#CCCCCC"))
        dc.DrawRectangle(0,0, TIMELINE_SIZE[0]*self.zoom,TIMELINE_SIZE[1])

        for i in range(TIME_TOTAL):
            dc.DrawText("%d:00" % (i), 
                        TIMELINE_POS[0]+((i*TIMELINE_MINUTE)*self.zoom),
                        TIMELINE_POS[1])

            
    def squares(self,dc):
        x, y = self.GetSize()         
        for i in range(0,x*self.zoom,GRID_STEP):
            dc.SetPen(wx.Pen("#333333",1))
            dc.DrawLine(0,TIMELINE_SIZE[1]+i, x,TIMELINE_SIZE[1]+i)      ### HORIZONTAL LINES
            dc.DrawLine(+i*self.zoom,30, +i*self.zoom,y)   ### VERTICAL LINES
            
        for i in range(0,x*self.zoom,TIMELINE_MINUTE):                 ### marqueur de minutes
            dc.SetPen(wx.Pen("#333333",3))
            dc.DrawLine(i*self.zoom,30, i*self.zoom,y)   ### VERTICAL LINES 
        

    def clip(self,pos):

        pos = list(pos)
        if pos[0] < 0:
            pos[0] = 0
            
        elif pos[0] > GRID_SIZE[0]:
            pos[0] = GRID_SIZE[0]
            
            
        if pos[1] < TIMELINE_SIZE[1]:
            pos[1] = TIMELINE_SIZE[1]
            pos[1] = pos[1] - (pos[1] % GRID_STEP)
            
        elif pos[1] > GRID_SIZE[1]:
            pos[1] = GRID_SIZE[1]
            pos[1] = pos[1] - (pos[1] % GRID_STEP)
            
        else:
            pos[1] = pos[1] - (pos[1] % GRID_STEP)
            
        return tuple(pos)
            
    def setZoom(self,x):
        self.zoom = x
        

    def getRectID(self,pos):
        for rec in self.rectangles:
            x = pos[0]
            y = pos[1]
            if rec.ContainsXY(x*self.zoom,y):      ## determine si le curseur a cliqué dans un rectangle
                print "ATTRAPPE: ", rec
                return self.rectangles.index(rec)
            else:
                return -1

class Rectangle(wx.Rect):
    def __init__(self, X,Y,width,heigth):
        wx.Rect.__init__(self, X, Y, width, heigth)
        self.X = X
        self.Y = Y
        self.width = width
        self.heigth = GRID_STEP
        
        
    def draw(self,dc,zoom,pen,brush):
        dc.SetPen(wx.Pen(pen,1)) 
        dc.SetBrush(wx.Brush(brush)) 
        dc.DrawRectangle(self.X*zoom,self.Y,self.width*zoom,self.heigth)
        
    def getTrackNum(self):
        self.trackNum = self.Y / self.heigth - 1 
        return self.trackNum    