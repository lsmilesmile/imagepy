# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 23:23:30 2017

@author: yxl
"""
import wx, os, sys
import time, threading
from .. import IPy, root_dir
# TODO: @2017.05.01
#from ui import pluginloader, toolsloader
from . import pluginloader, toolsloader, widgetsloader
from ..core.manager import ConfigManager, PluginsManager, TaskManager, WindowsManager
from ..core.engine import Macros
import wx.aui as aui

class FileDrop(wx.FileDropTarget):
    def OnDropFiles(self, x, y, path):
        print(["Open>{'path':'%s'}"%i for i in path])
        Macros('noname', ["Open>{'path':'%s'}"%i.replace('\\', '/') for i in path]).start()
        return 0

class ImagePy(wx.Frame):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = 'ImagePy', 
                            size = wx.Size(-1,-1), pos = wx.DefaultPosition, 
                            style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.auimgr = aui.AuiManager()
        self.auimgr.SetManagedWindow( self )
        self.auimgr.SetFlags(aui.AUI_MGR_DEFAULT)

        logopath = os.path.join(root_dir, 'data/logo.ico')
        #self.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_3DLIGHT ) )
        self.SetIcon(wx.Icon(logopath, wx.BITMAP_TYPE_ICO))
        self.SetSizeHints( wx.Size( 600,-1 ), wx.DefaultSize )
        IPy.curapp = self
        # Todo:Fixed absolute/relative path!
        # print("menuspath:{}".format( os.path.join(root_dir,"menus")))
        # print("toolspath:{}".format(os.path.join(root_dir,"tools"))
        # menuspath = os.path.join(root_dir, "menus")
        # toolspath = os.path.join(root_dir,"tools")
        self.menubar = pluginloader.buildMenuBarByPath(self, 'menus')
        self.SetMenuBar( self.menubar )
        self.shortcut = pluginloader.buildShortcut(self)
        self.SetAcceleratorTable(self.shortcut)
        #sizer = wx.BoxSizer(wx.VERTICAL)
        self.toolbar = toolsloader.build_tools(self, 'tools')

        self.auimgr.AddPane(self.toolbar, wx.aui.AuiPaneInfo() .Left() .PinButton( True )
            .Dock().Resizable().FloatingSize( wx.Size( 48,520 ) ).Layer( 10 ) )
        
        self.widgets = widgetsloader.build_widgets(self, 'widgets')
        self.auimgr.AddPane( self.widgets, wx.aui.AuiPaneInfo() .Right().Caption('Widgets') .PinButton( True )
            .Dock().Resizable().FloatingSize( wx.DefaultSize ).MinSize( wx.Size( 266,-1 ) ) .Layer( 10 ) )
        
        self.load_aui()
        self.load_dev()
        


        #sizer.Add(self.toolbar, 0, wx.EXPAND, 5 )
        #self.line_color = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        #self.line_color.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHT ) )
        #sizer.AddStretchSpacer(prop=1)
        #sizer.Add(self.line_color, 0, wx.EXPAND |wx.ALL, 0 )
        stapanel = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        sizersta = wx.BoxSizer( wx.HORIZONTAL )
        self.txt_info = wx.StaticText( stapanel, wx.ID_ANY, "ImagePy  v0.2", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txt_info.Wrap( -1 )
        #self.txt_info.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_INFOBK ) )
        sizersta.Add( self.txt_info, 1, wx.ALIGN_BOTTOM|wx.BOTTOM|wx.LEFT|wx.RIGHT, 2 )
        self.pro_bar = wx.Gauge( stapanel, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size( 100,15 ), wx.GA_HORIZONTAL )
        sizersta.Add( self.pro_bar, 0, wx.ALIGN_BOTTOM|wx.BOTTOM|wx.LEFT|wx.RIGHT, 2 )
        stapanel.SetSizer(sizersta)
        stapanel.SetDropTarget(FileDrop())
        self.auimgr.AddPane( stapanel, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).PinButton( True ).Dock()
            .PaneBorder( False ).Resizable().BestSize( wx.Size( -1,-1 ) ).DockFixed( True ).Layer( 10 ) )
        
        #sizer.Add(stapanel, 0, wx.EXPAND, 5 )
        #self.SetSizer( sizer )

        self.Centre( wx.BOTH )
        self.Layout()
        self.auimgr.Update()
        self.Fit()
        self.update = False

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind( wx.aui.EVT_AUI_PANE_CLOSE, self.on_panel_closed)
        thread = threading.Thread(None, self.hold, ())
        thread.setDaemon(True)
        thread.start()

    def on_panel_closed(self, event):pass

    def load_aui(self):
        
        self.canvasnb = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        self.auimgr.AddPane( self.canvasnb, wx.aui.AuiPaneInfo() .Center() .CaptionVisible( False ).PinButton( True ).Dock()
            .PaneBorder( False ).Resizable().FloatingSize( wx.DefaultSize ) )
        self.canvasnb.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_pagevalid)
        self.canvasnb.Bind( wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_pageclosed)

    def load_dev(self):
        return
        self.devpan = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE )
        self.auimgr.AddPane( self.devpan, wx.aui.AuiPaneInfo() .Bottom() .CaptionVisible( False ).PinButton( True ).Dock()
            .PaneBorder( False ).Resizable().FloatingSize( wx.DefaultSize ) )

    def on_pagevalid(self, event):
        WindowsManager.add(event.GetEventObject().GetPage(event.GetSelection()))
        
    def on_pageclosed(self, event):
        WindowsManager.remove(event.GetEventObject().GetPage(event.GetSelection()))

    def reload_plugins(self):
        for i in range(self.menubar.GetMenuCount()): self.menubar.Remove(0)
        # menuspath = os.path.join(root_dir,"menus")
        pluginloader.buildMenuBarByPath(self, "menus", self.menubar)

    def hold(self):
        dire = 1
        while True:
            try:
                if time == None: break
                time.sleep(0.05)
                tasks = TaskManager.get()
                if(len(tasks)==0):
                    if self.pro_bar.IsShown():
                        wx.CallAfter(self.set_progress, -1)
                    continue
                arr = [i.prgs for i in tasks]
                if (None, 1) in arr:
                    if self.pro_bar.GetValue()<=0:
                        dire = 1
                    if self.pro_bar.GetValue()>=100:
                        dire = -1
                    v = self.pro_bar.GetValue()+dire*5
                    wx.CallAfter(self.set_progress, v)
                else:
                    v = max([(i[0]+1)*100.0/i[1] for i in arr])
                    wx.CallAfter(self.set_progress, v)
            except: 
                pass
    def set_info(self, value):
        self.txt_info.SetLabel(value)

    def set_progress(self, value):
        v = max(min(value, 100), 0)
        self.pro_bar.SetValue(v)
        if value==-1:
            self.pro_bar.Hide()
        elif not self.pro_bar.IsShown():
            self.pro_bar.Show()
        self.pro_bar.Update()

    def set_color(self, value):
        self.line_color.SetBackgroundColour(value)

    def on_close(self, event):
        ConfigManager.write()
        self.Destroy()
        sys.exit()

    def __del__( self ):
        pass

if __name__ == '__main__':
    app = wx.App(False)
    mainFrame = ImagePy(None)
    mainFrame.Show()
    app.MainLoop()
