'''
This is opencv module for Python/vapoursynth scripts that previews VideoNode (clip) within script itself by just running script.
It is a pythonic solution to play or compare vapoursynth clips by using opencv module.
'''

import os
import sys
import platform
import timeit


import vapoursynth as vs
from vapoursynth import core
import numpy as np
import cv2
try:
    from distutils.version import StrictVersion
    if StrictVersion(cv2.__version__) < StrictVersion('3.4.1'):
        raise Exception('\n'+  f'openCV version is {cv2.__version__}, it needs to be at least 3.4.1')
except ImportError:
    pass
        
#optional for windows or linux but needed for darwin platform to figure out free RAM        
try:
    import psutil
except ImportError:
    pass


RESPECT_X_SUBSAMPLING = True                       #leave both True if wanting snapping to legit cropping values for Vapoursynth based on clip subsampling
RESPECT_Y_SUBSAMPLING = True                       #user can override these with:  Preview([clip], ignore_subsampling = True)

                                                   #assigning keys '1','2','3',...'9', '0' to rgb clip indexes 0,1,2,..., 8, 9
CLIP_KEYMAP = [ ord('1'), ord('2'), ord('3'), ord('4'), ord('5'), ord('6'), ord('7'), ord('8') ,ord('9'), ord('0') ]


WINDOWS_KEYMAP =  {
            
                 ord(' ') : 'pause_play',          #spacebar as a switch for play and pause
                 ord(',') : 'left_arrow',          #key ',' or '<'
                 ord('.') : 'right_arrow',         #key '.' or '>'
                       
                       13 : 'execute_cropping',    #key 'Enter' , right mouse click also executes cropping
                  2359296 : 'home',                #key 'Home' -  first video frame
                  2293760 : 'end',                 #key 'End'- last video frame
                 ord('y') : 'object_step_up',      #key 'y' selected object to move step up
                 ord('n') : 'object_step_down',    #key 'h' selected object to move step down
                 ord('g') : 'object_step_left',    #key 'g' selected object to move step left
                 ord('j') : 'object_step_right',   #key 'j' selected object to  move step right
                 ord('p') : 'frame_props',         #key 'p' to print frame properties
                 ord('z') : 'quick_2x_zoom_in',    #key 'z' zooming 2x
                 ord('i') : 'pixel_info',          #key 'i' print pixel info under mouse: pixel coordinates, frame#, YUV and RGB values
                 ord('r') : 'reset_preview',       #key 'r' reseting preview
                 ord('e') : 'write_image',         #key 'e' to write showing frame you have on screen as png to hardisk, what you see
                 ord('w') : 'write_image_1_to_1',  #key 'w' to write showing frame you have on screen as png to hardisk, image is 1:1, ignores zooms in blowup
                 ord('q') : 'closing',             #key 'q'   to quit
                       27 : 'zoom_out',            #key 'Esc' to go back to previous zoom or crop
                 ord('s') : 'slider_switch',       #key 's' slider on/off, to show slider or to destroy it
                 ord('f') : 'fullscreen_switch',   #key 'f' fullscreen on/off
                 ord('h') : 'help'                 #key 'h' help, shows hotkeys for keybinding
                 
                   }


LINUX_KEYMAP  =   {
            
##                    65361 : 'left_arrow', #81
##                    65362 : 'up_arrow',   #82
##                    65363 : 'right_arrow',#83
##                    65364 : 'down_arrow', #84
                 ord(' ') : 'pause_play',
                 ord(',') : 'left_arrow',
                 ord('.') : 'right_arrow',
                       13 : 'execute_cropping',
                    65360 : 'home',
                    65367 : 'end',
                 ord('y') : 'object_step_up',
                 ord('n') : 'object_step_down',
                 ord('g') : 'object_step_left',
                 ord('j') : 'object_step_right',
                 ord('p') : 'frame_props',
                 ord('z') : 'quick_2x_zoom_in',
                 ord('i') : 'pixel_info',
                 ord('r') : 'reset_preview',
                 ord('e') : 'write_image',
                 ord('w') : 'write_image_1_to_1',
                 ord('q') : 'closing',
                       27 : 'zoom_out',
                 ord('s') : 'slider_switch',
                 ord('f') : 'fullscreen_switch',
                 ord('h') : 'help'
                      }
        
    
DARWIN_KEYMAP  =  {

                 ord(' ') : 'pause_play',
                 ord(',') : 'left_arrow',
                 ord('.') : 'right_arrow',
                       13 : 'execute_cropping',
                    65360 : 'home',
                    65367 : 'end',
                 ord('y') : 'object_step_up',
                 ord('n') : 'object_step_down',
                 ord('g') : 'object_step_left',
                 ord('j') : 'object_step_right',
                 ord('p') : 'frame_props',
                 ord('z') : 'quick_2x_zoom_in',
                 ord('i') : 'pixel_info',
                 ord('r') : 'reset_preview',
                 ord('e') : 'write_image',
                 ord('w') : 'write_image_1_to_1',
                 ord('q') : 'closing',
                       27 : 'zoom_out',
                 ord('s') : 'slider_switch',
                 ord('f') : 'fullscreen_switch',
                 ord('h') : 'help'
                      }


TRANSFER =     {
                #transfer_in or transfer : transfer_in_s or transfer_s
                0:'reserved',
                1:'709',
                2:'unspec',
                3:'reserved',
                4:'470m',
                5:'470bg',
                6:'601',
                7:'240m',
                8:'linear',
                9:'log100',
                10:'log316',
                11:'xvycc',
                13:'srgb',
                14:'2020_10',
                15:'2020_12',
                16:'st2084',
                18:'std-b67'
                }                             


MATRIX =      {
                #matrix_in or matrix : matrix_in_s or matrix_s
                0:'rgb',
                1:'709',
                2:'unspec',
                3:'reserved',
                4:'fcc',
                5:'470bg',
                6:'170m',
                7:'240m',
                8:'ycgco',
                9:'2020ncl',
               10:'2020cl' ,
               12:'chromancl',
               13:'chromacl',
               14:'ictcp'
              }   


PRIMARIES =   {
                #primaries_in or primaries : primaries_in_s or primaries_s
                1 : '709'    ,
                2 : 'unspec' ,
                4 : '470m'   ,
                5 : '470bg'  ,
                6 : '170m'   ,
                7 : '240m'   ,
                8 : 'film'   ,
                9 : '2020'   ,
               10 : 'st428'  , #'xyz'
               11 : 'st431-2',
               12 : 'st432-1',
               22 : 'jedec-p22'
                }

PROPS = {
            '_ChromaLocation':  {0:'left', 1:'center', 2:'topleft', 3:'top', 4:'bottomleft', 5:'bottom'},
            '_ColorRange':      {0:'full range', 1:'limited range'},
            '_Matrix':           MATRIX    ,
            '_Primaries':        PRIMARIES ,
            '_Transfer':         TRANSFER  ,
            '_FieldBased':      {0:'progressive', 1:'bottom field first', 2:'top field first'},
            '_AbsoluteTime':    {},
            '_DurationNum':     {},
            '_DurationDen':     {},
            '_Combed':          {},    
            '_Field':           {0:'from bottom field, if frame was generated by SeparateFields',
                                  1:'from top field, if frame was generated by SeparateFields'},
            '_PictType':        {},
            '_SARNum':          {},
            '_SARDen':          {},
            '_SceneChangeNext': {0:'nope',1:'LAST FRAME of the current scene'},
            '_SceneChangePrev': {0:'nope',1:'FRAME STARTS a new scene'},
            '_Alpha':           {}
        } 



ERROR_FILENAME_LOG = 'error_NO_output_window.txt'

HOTKEYS_HELP ='''KEYBINDING:
'1' to '9' or '0' to switch between clips to compare them if loading more clips.
           So there is max 10 clips. But technically,
           it could be more if keybinding is adjusted.
MOUSE LEFT DOUBLECLICK  zooms in 2x, centers on mouse position
'Z'  zooms in 2x as well, again centers on mouse position

MOUSE LEFT CLICK and MOVE  initiates crop mode, selecting rectangle with mouse,
     confirm selection  with ENTER KEY or doubleclicking within selection or with RIGHT MOUSE CLICK,
     while touching first point, it snaps to to a pixel following subsumpling (max from loaded clips),
     also while drawing a rectangle , it snaps to mods passed as argument, (recomended values 2,4,8 or 16)
     default mods:  mod_x=2, mod_y=2 
'R'  RESETs preview to original
','  '<'  step one frame back
'.'  '>'  step one frame forward
'Home' go to first frame
'End'  go to last frame
     Seeking is source plugin dependant so it could take a time to request a frame.
'Q'  quit app, but if zoom or crop was applied, it just resets to original clip first
'Esc' preview goes back to previous zoom or crop
'I'  prints YUV or RGB values for pixel under mouse pointer in preview window
     printing is in this format:
     clip number, pictur type, frame number ,absolute pixel coordinates, original clip YUV or RGB values 
     or preview RGB values
'P'  prints all available frame properties (_PictType, _Matrix, _Primaries ...etc.)
     http://www.vapoursynth.com/doc/apireference.html#reserved-frame-properties
'W'  save PNG image, what you just preview and it will be saved on hardisk as 8bit PNG as 1:1, ingnoring zoom that you have on screen
'E'  save PNG image, what you just preview and it will be saved on hardisk as 8bit PNG, it will be saved as you see on screen, respecting zoom, pixel blocks
'Spacebar'   Play/Pause switch 
'S'  Slider on/off,
     Using slider - grab slider , move it to a frame.
     Seeking is video and vapoursynth source plugin dependant or its argument selection,
     you could experiance conciderable delay and freeze
'F'  Fullscreen on/off switch
'H'  help, prints this KEYBINDING text

During cropping and just before confirming that crop,
any selected object is defined by clicking on a 'corner' or 'line' or 'all' (clicking within selected rectangle)
So selected rentagle could be manualy re-defined by moving that object up, down, lef or right one step

'Y'  selected object to move step up 
'N'  selected object to move step down
'G'  selected object to move step left
'J'  selected object to  move step right
'''


        
class Preview:
    '''
    --- previewing vapoursynth videonodes/clips by opencv(at least 3.4.1 version needed)
    --- comparing, swapping, previewing vapoursynth clips by pressing  assigned keys on keyboard (1 - 9)
    --- clip switching is smooth, seamless during playback
    --- with slider or without
    --- printing , previewing pixel values for YUV, RGB or other vapoursynth formats, readings could be for example:
        clip 1: I Frame: 2345     Pixel: 411,129   CompatYUY2: y:171  u:104  v:160    RGB24: r:233  g:164  b:128
    --- printing all available properties for a frame (props)
    --- QUICK zooming/cropping,  2x, by mouse doubleclick, centered to mouse position
    --- or MANUAL cropping/zooming by drawing cropping area on screen, when all corners, lines could be adjusted
        or selected area could be moved/panned,
    --- all crops and zoom snap to  mods and subsumpling for YUV clips (could be turned off: mod_x=1, mod_y=1, ignore_subsampling=True)
    --- using SHIFT key while selecting, cropping area is snapping to original clip's aspect ratio
    --- all crops and zoom show real core.std.CropAbs(), vapoursynth command,  to obtain that crop, or even live feedback during selection
    --- returning back to previous zoom or crop (pressing 'Esc')
    --- writing PNG images to hardisk (what you see, gets saved (with blow-up pixels) or what you see 1:1),
    --- when writing PNG images during playback it writes subsequent PNG's (for gif creation or other purposes)
    '''
    
    def __init__(self, clips,
                 frames=None, delay = None, img_dir=None, matrix_in_s=None, kernel='Point',
                 mod_x=2, mod_y=2, ignore_subsampling=False,
                 position = (60,60), preview_width = None, preview_height = None,
                 output_window=False, fullscreen=False, play=False, slider=False):

        #setting output print first
        self.validate_boolean(dict(output_window=output_window))

        error_message = ''        
        if output_window:
            try:
                import tkinter
            except ImportError:
                raise Exception("No standard library tkinter module in PATH\n output_window=True needs python's tkinter module to create output window")      
            try:
                import output_window
            except ImportError:
                error_message  = ( 'No module output_window.py in PATH\n'
                                   'Using with Vapoursynth Editor:\n'
                                   'you can put output_window.py into script\'s directory or add that directory to sys.path:\n'
                                   'import sys\n'
                                   'import os\n'
                                   'sys.path.append(os.path.abspath("...your path to directory ..."))\n'
                                 )
                self.log('No module output_window.py in PATH\n')         
                with open(ERROR_FILENAME_LOG, 'a') as info:
                    info.write('[view]\n' + error_message )
                

        self.clips_orig          =  clips
        self.frames              =  frames
        self.delay               =  delay
        self.matrix_in_s         =  matrix_in_s
        self.kernel              =  kernel
        self.img_dir             =  img_dir
        self.modx                =  mod_x
        self.mody                =  mod_y
        self.position            =  position
        self.init_preview_width  =  preview_width
        self.init_preview_height =  preview_height
        self.fullscreen          =  fullscreen
        self.play                =  play
        self.slider              =  slider
        self.ignore_subsampling  =  ignore_subsampling
        try:
            self.validate_clips()
        except ValueError  as err:
            raise ValueError('[Preview]:', err)
   
        self.validate_frames()
        self.validate_delay()
        self.validate_img_dir()
        self.validate_matrix()
        self.validate_kernel()
        self.validate_position()
        self.validate_preview_dimensions()
        self.validate_boolean(dict(fullscreen=fullscreen, play=play, slider=slider, ignore_subsampling=ignore_subsampling))


        #limiting Vapoursynth cache if not enough RAM'''
        available = None
        available_RAM = self.freeRAM()
        vapoursynth_cache = core.max_cache_size
        self.log(f'Vapoursynth cache is set to: {vapoursynth_cache}MB')
        if available_RAM:
            self.log(f'free RAM: {available_RAM}MB')
            cache = self.limit_cache(vapoursynth_cache, available_RAM)
            if not cache == vapoursynth_cache:
                self.log(f'setting Vapoursynth cache to: {cache}MB\n')
                core.max_cache_size = cache
        else:
            self.log('\nWARNING, failed to get available free RAM,')
            self.log('         Vapoursynth cache was not limited if needed,')
            self.log('         RAM overrun or freeze possible\n')          


        #converting clips to RGB clips for opencv preview
        self.rgbs           = []               #currently previewing rgb clips
        self.rgbs_orig      = []               #back ups of original rgb clips
        self.rgbs_error     = []               #list of booleans, True if rgb had errors
        convert = Conversions()        
        depth = 8                              #openCV would scale 16bit int or 32bit float to 0-255 anyway
        sample_type = vs.INTEGER
        
        def error_clip(err):
            err_clip = core.std.BlankClip(self.clips_orig[i],  format=vs.RGB24)
            err_clip = core.text.Text(err_clip, err)   
            self.rgbs.append(err_clip)
            self.rgbs_error.append(True)
        
        for i, clip in enumerate(self.clips_orig):
            rgb, log = convert.toRGB(clip, matrix_in_s=self.matrix_in_s, depth=depth, kernel=self.kernel, sample_type = sample_type)
            log = 'clip {} to RGB for preview:\n'.format(i+1) + log
            
            try:
                rgb.get_frame(0)
            except vs.Error as err:
                log += '\n[toRGB]'+ str(err)
                error_clip(err)
            else:    
                if isinstance(rgb, vs.VideoNode):
                    self.rgbs.append(rgb)
                    self.rgbs_error.append(False)
                else:
                    err = '\n[toRGB] converted RGB is not vs.VideoNode'
                    log += err
                    error_clip(err)              
            self.log(log)
                        
        if self.rgbs:     
            self.modx, self.mody, self.modx_subs, self.mody_subs = self.validate_mod(self.modx, self.mody)
            self.rgbs_orig = self.rgbs.copy() 
            self.show()
  
        else:
            self.log('[Preview.__init__] no clips loaded ')
            
                    
    def show(self):
        '''
        setting up show loop
        '''
        #self.log('\n[Preview.show]')
        #getting keymap and indexMap depending on OS
        OS = self.get_platform()      
        self.windows_keymap = WINDOWS_KEYMAP
        self.linux_keymap = LINUX_KEYMAP
        self.darwin_keymap = DARWIN_KEYMAP
        KEYMAP   = getattr(self, OS + '_keymap')       

        #loop properties 
        self.close = False                              # True will exit a show, app
        self.frame = self.frames[0]                     # starting frame 
        self.i  = 0                                     # self.i is current previewing clip index
        j = 0                                           # tracks clip changes, if it matches self.i 
        if self.play:    self.play  = 1                 # make bint from bool
        else:            self.play  = 0
        self.previewData_reset()                        #makes first stored crop data (width, height, left, top)
        
        self.width  = self.rgbs_orig[self.i].width
        self.height = self.rgbs_orig[self.i].height
        self.left   = 0
        self.top    = 0
        
        #mouseAction() properties
        self.ix, self.iy = (-1 , -1)     #assuming mouse off preview area so no readings yet
        self.tx, self.ty = (-10,-10)     #first touchdown coordinates while drawing rectangle
        self.isCropping = False          #initiates cropping
        self.drawing = False             #True after left mouse button clicks so cropping drawing animation is activated
        self.panning = False             #selected rectangle object for moving any direction - panning            
        self.execute_crop = False        #True executes selected cropping for all videos
        self.object = None               #name of object, used in manual step correction using keys
        self.proximity = 10              #while clicking down it will pick up corner, line or selection with this pixel proximity in that order
        self.good_c = (0,255,0)          #BGR color for selection lines if crop is ok in vapoursynth
        self.bad_c = (0,0,255)           #lines turn into this BGR color if cropping would give error in vapoursynth
        self.color = self.good_c
        self.flash_color = (255,255,255) #flashing color after selecting an object (a line, lines,  corner)
        self.x1 = None                   #left selection x coordinate and also a flag if there was a selection
          
        #opencv window
        text=''
        for i , rgb in enumerate(self.rgbs):
            text +='clip{} {}    '.format(i+1, self.clips_orig[i].format.name)
        clip_KEYMAP = CLIP_KEYMAP[:len(self.rgbs)]
        
        self.title = 'VideoNodes:   {}'.format(text)
        self.build_window(self.title, self.mouseAction)
        self.log('OpenCV version: ' + cv2.__version__)
        try:
            cv2.displayStatusBar(self.title, '')
            self.Qt = True
        except:
            self.print_info('  No Status Bar,  This OpenCV was compiled without QT library')
            self.Qt = False
        self.placement = (self.position[0], self.position[1], self.init_preview_width, self.init_preview_height)
        if not self.fullscreen:
            cv2.resizeWindow(self.title, self.init_preview_width, self.init_preview_height)
            cv2.moveWindow(self.title, self.position[0],self.position[1])
        if self.slider:
            self.build_slider()

        #print clip resolutions if different in clips 
        if not len(set(self.resolutions)) <= 1:
            self.log(f"Clips DO NOT HAVE THE SAME RESOLUTIONS, expect weird behaviour if cropping")
        
        #init print  
        self.print_info(self.print_clip_name() +': {}'.format(self.i+1))

        if self.play: self.ref = timeit.default_timer()                    #starting time reference for timing frames
        
        '''
        main openCV playback loop
        '''
        while True:
            
            self.show_frame()
            if self.slider:
                cv2.setTrackbarPos('Frames', self.title, self.frame)
            key = cv2.waitKeyEx(self.play)
            #print(key)
            if key != -1:                                                  #if a key was pressed
                try:
                    getattr(self, KEYMAP[key])()                           #execute functions for hotkeys
                except KeyError:             
                    try:
                        self.i = clip_KEYMAP.index(key)               #if key was pressed that suppose to change clips, change index for clips
                    except ValueError:
                        pass
                    else:
                        #print this only one time
                        if self.i!= j:
                            self.print_info(self.cropping_line_text(*self.previewData[-1]))    
                            j=self.i
                        
                if self.close:
                        break                                              #exiting loop and app
                        
            self.frame = self.update_frame(self.frame)

            if cv2.getWindowProperty(self.title, cv2.WND_PROP_VISIBLE) < 1:   #canceling window clicking 'x'
                 break

        cv2.destroyAllWindows()
        
    def update_frame(self, f):    
        if self.play :
            f += 1
        if f >= self.frames[1]:
            self.play  = 0
            f = self.frames[1]-1
        elif f < self.frames[0]:
            self.play = 0
            f = self.frames[0]
        return f
        
    def show_frame(self):
        '''
        Vapoursynth frame is converted  to numpy arrays for opencv to show
        delay is handled here, not in cv2.waitKey() because timeit.default_timer() takes app&system  time overhead into an account
        '''
        
        try: 
            f = self.rgbs[self.i].get_frame(self.frame)
        except:       
            f = self.error_frame()                          
        self.img = np.dstack([np.array(f.get_read_array(p), copy=False) for p in [2,1,0]])
        if self.isCropping and self.x1 is not None:
            img = self.img_and_selection(self.img, (self.x1,self.y1,self.x2,self.y2),self.color)
            if self.play: self.delay_it()
            cv2.imshow(self.title, img)
        else:
            if self.play: self.delay_it()
            cv2.imshow(self.title, self.img)
            
    def error_frame(self):
        self.play = 0
        def log_err():
            err = '\n' + str(sys.exc_info()[0])+'\n'
            err += 'in line ' + str(sys.exc_info()[2].tb_lineno)+'\n'
            err += str(sys.exc_info()[1])+'\n'
            return err
        err = log_err()
        info = '\nclip: {}  Frame: {} ,Frame could not be rendered for this clip'.format(self.i, self.frame)
        self.log(err+info)
        if self.Qt: self.print_statusBar(info)
        err_clip = core.std.BlankClip(self.clips_orig[self.i],  format=vs.RGB24, length=1).text.Text(err+info)
        return err_clip.get_frame(0)
    
    def delay_it(self):       
        while True:
           new = timeit.default_timer()
           if new >= self.ref + self.delay:
               self.ref = new
               break        

    def get_platform(self):
        '''
        sys.platform gets 'Linux', 'Windows' or 'Darwin'
        retuns: 'linux', 'windows' or 'darwin'  
        '''
        OS = None
        if sys.platform.startswith('linux'):
            OS = 'linux'
        elif sys.platform.startswith('win'):
            OS = 'windows'
        elif sys.platform == 'darwin':
            OS = 'darwin'
        else:
            try:
                OS = platform.system()
            except:
                OS = None
        if OS: return OS.lower()
        else: return None    
    
    def execute_cropping(self):
        if self.execute_crop:
            self.crop_to_new(self.width, self.height, *self.get_absolute_offsets(self.x1, self.y1))
            self.isCropping = False
            self.execute_crop = False
            
    def pause_play(self):
        if self.play:
            self.play = 0
        else:
            self.play = 1
            self.ref = timeit.default_timer()       
            
    def log(self, *args):
        '''
        if
        argument output_window = True
        and
        output_window modul is imported,
        then print is redirected to tkinter window
        '''
        text =''
        for item in args:
            try:
                text += str(item) + ' '
            except:
                pass        
        print(text[:-1])

    def frame_props(self):
        self.log(f'\nclip{self.i+1} {self.clips_orig[self.i].format.name}, properties of frame {self.frame}:')
        self.log(self.get_frame_props(self.clips_orig[self.i], self.frame))
       
    def get_frame_props(self, clip, frame):
        '''
        prints all available frame properties (_PictType, _Matrix, _Primaries ...etc.)
        http://www.vapoursynth.com/doc/apireference.html#reserved-frame-properties
        '''

        info = []
        props_dict = dict(clip.get_frame(frame).props)
        for prop, prop_value in props_dict.items():
            if isinstance(prop_value, bytes):
                prop_value = prop_value.decode()
                
            elif isinstance(prop_value, vs.VideoFrame):  #this is a wild guess for alpha, did not look into it yet
                prop_value = 'yes'
                
            info.append('  {: <25}{}'.format(prop, prop_value))
            try:
                info.append('={}'.format(PROPS[prop][prop_value]))
            except:
                pass
            info.append('\n')            
        return ''.join(info)     


    def mouseAction(self,event,x,y,flags,p=None):
        '''
        Mouse click initiates drawing of a cropping rectangle.
        While holding SHIFT, new rectangle snaps to aspect ration of a clip.
        Drawing of rectangle respects and snaps to original YUV clip's subsampling.
               (if not deactivated by: mod_x=1, mod_y=1, ignore_subsampling=True) 
        Clicking outside of selected rentangle cancels cropping.
               (or initiates new cropping selection if mouse keeps moving)
        Double click inside of selected rentangle (or keyboard ENTER) confirms and performs crop.
        Clicking once inside of selected rentangle activates selection for moving,
        that could be done by mouse or just using keyboard ('g','y','j','n' - one step to left,top,right or down),
        to move it in smallest subsampling steps.
        Clicking on particular single object (corner or a line) also activates moving but only for that object.
        
        mouseAction needs globals so using Preview class attributes for that purpose to store values:
        ix, iy         mouse position
        xa,ya          first anchor point for drawing selection
        x1,x2,y1,y2    current selection points (rectangle)
        width, height  width which is (x2-x1) and height (y2-y1) ,for current rectangle      
        '''
        if event == cv2.EVENT_LBUTTONDOWN:
            self.useX = True
            self.useY = True
            
            if not self.isCropping:
                self.isCropping   = True
                self.drawing      = True
                self.execute_crop = False               
                self.init_new_selection(x,y)
                
            elif self.isCropping:
                self.drawing = True                
                self.object  = self.select_object(x,y)
                if self.object == 'all':           #whole selection selected, set for panning
                    self.panning = True
                elif self.object is None:          #none object selected, initiate new crop
                    self.execute_crop = False
                    self.x1 = None                 #for show_frame() to not show selection, cannot use isCropping switch, it could be True
                    self.init_new_selection(x,y)                    

        elif event == cv2.EVENT_MOUSEMOVE:
            self.ix = x        
            self.iy = y
                
            if self.isCropping and self.drawing and not self.panning:
                rectangle = self.new_rectangle(x,y,flags&cv2.EVENT_FLAG_SHIFTKEY)
                self.live_crop_info(rectangle)
                if not self.play:
                    cv2.imshow(self.title, self.img_and_selection(self.img,rectangle,self.color))              
                
            elif self.panning:
                rectangle = self.move_rectangle(x,y,flags&cv2.EVENT_FLAG_SHIFTKEY)
                self.live_crop_info(rectangle)
                if not self.play:
                    cv2.imshow(self.title, self.img_and_selection(self.img,rectangle,self.color))              
                
        elif event == cv2.EVENT_LBUTTONUP:
            self.panning = False
            self.drawing = False
            if self.tx == x and self.ty == y:      #mouse touched screen but did not moved, no drawing happened, quit cropping 
                self.isCropping = False                
                self.print_info(self.cropping_line_text(*self.previewData[-1]))
                self.show_frame()
                self.ix = x        
                self.iy = y
                
            elif self.isCropping:                  #rectangle is selected, relevant atributes ready for crop: self.x1,self.y1,self.x2,self.y2
                self.execute_crop = True           #but self.isCropping is still True because cropping can be modified
                                                   #self.isCropping becomes False only after user executes cropping (key Enter or dbl click or right mouse click)                                                                          
        elif event == cv2.EVENT_LBUTTONDBLCLK:
            if self.isCropping:                    #doubleclick into selected area would make crop
                self.execute_crop = False
                self.isCropping = False   
                self.crop_to_new(self.width, self.height, *self.get_absolute_offsets(self.x1, self.y1))
                self.show_frame()
                self.ix = x        
                self.iy = y
            else:                                  #doubleclick outside of  selected area or if there is no selection
                self.quick_2x_zoom_in(x,y)         #quick 2x zoom, centered to mouse position x,y
                #self.show_frame()                 #cv2.EVENT_LBUTTONUP renders frame because self.tx == x and self.ty == y                
                
        elif event == cv2.EVENT_RBUTTONDOWN:       #if rectangle is drawn for crop, right doubleclick executes crop
            if self.execute_crop:
                self.execute_crop = False
                self.isCropping = False
                self.crop_to_new(self.width, self.height, *self.get_absolute_offsets(self.x1, self.y1))
                self.show_frame()
                self.ix = x        
                self.iy = y
                
    def init_new_selection(self, x,y):
        '''initiate drawing of selection area by creating first anchor point and other properties'''
        self.tx = x 
        self.ty = y
        #self.play = 0                            #stopping playback while starting to crop
        self.w      = self.rgbs[self.i].width
        self.h      = self.rgbs[self.i].height
        self.origw = self.rgbs_orig[self.i].width
        self.origh = self.rgbs_orig[self.i].height            
        self.xa = x - x % self.modx_subs          #snapping to correct subsumpling column
        self.ya = y - y % self.mody_subs          #snapping to correct subsumpling line

        
    def new_rectangle(self,x,y, flags=0):
        '''
        draw a rectangle selection x1,y1; x2,y2 , snapping to video resolution mods and subsampling mods
        keep selection within rgb's dimensions w,h
        if SHIFT is pressed keep clips aspect ratio (and of course keep mods as well!)
        also xa,ya is always needed, that is anchor point for selection, first point of selection
        '''

        if self.useX:
            if x>=self.xa: 
                x1 = self.xa 
                x2 = min(x, self.w)       
            else:
                x1 = max(x, 0)
                x2 = self.xa
            w = x2 - x1
            w = w - w % self.modx                                      
        else:
            x1 = self.x1
            x2 = self.x2                   
            
        if self.useY:
            if y>=self.ya:
                y1 = self.ya
                y2 = min(y, self.h)
            else:
                y1 = max(y, 0)
                y2 = self.ya                                                   
            h = y2 - y1
            h = h - h % self.mody                                      
        else:
            y1 = self.y1
            y2 = self.y2
            
        if flags == 16:       
            '''SHIFT key is pressed, snap rectangle into aspect ratio '''
            t_w = w
            ar = self.origh/self.origw
            while t_w > 0:
                t_h = t_w*ar
                if t_h.is_integer() and t_h % self.mody == 0 and t_h + y1 <= self.h and t_h <= y2:
                    h = int(t_h)
                    w = t_w
                    break
                t_w -= self.modx
            if t_w <= 0: w = 0
            
        #final correction
        if self.useX:
            if x>=self.xa: x2 = x1 + w
            else:          x1 = x2 - w
            self.width =  w
        if self.useY:
            if y>=self.ya: y2 = y1 + h
            else:          y1 = y2 - h
            self.height = h

        self.x1 = self.left = x1
        self.y1 = self.top =  y1
        self.x2 = x2
        self.y2 = y2
        
        return (x1,y1,x2,y2)

                
    def move_rectangle(self,x,y, flags=0):    
        '''
        move object 'all' (all lines ergo all selected area)
        which technically is making new rectangle x1,y1; x2,y2 but same width and height and snapping to subsampling mods,
        keep selection within rgb's dimensions w,h
        if SHIFT key is pressed while moving, slide selection horizontaly or verticaly only,
        dx (x - self.x1) and dy (y - self.y1) are introduced to imitate mouse always dragging x1,y1 to not have weird delays if dragging off screen 
        '''
        x1 = x - self.dx
        y1 = y - self.dy
        x1 = max((x1 - x1 % self.modx_subs), 0)
        if x1 + self.width > self.w:
            x1 = self.w-self.width
        
        y1 = max((y1 - y1 % self.mody_subs), 0)
        if y1 + self.height > self.h:
            y1 = self.h-self.height      
        if flags == 16:
            '''SHIFT key is pressed'''
            if abs(x1-self.xa) > abs(y1-self.ya):
                y1 = self.ya                          #anchor/freeze y
            else:
                x1 = self.xa                          #anchor/freeze x
        x2 = x1+self.width
        y2 = y1+self.height
        self.x1 = self.left = x1
        self.y1 = self.top =  y1
        self.x2 = x2
        self.y2 = y2
        return (x1,y1,x2,y2)

    def select_object(self, x,y):
        '''
        locate object with mouse click on x,y coordinates, it could be: a corner, line or middle of selection(object 'all')
        set that object for drawing/moving and  flash particular selected object,
        priority for selections: corner, then line, then selected area(object 'all')
        return found name of object
        '''
        p  = max(self.proximity,1)                 #proximity to "see" an object from that pixel distance when clicking
        f  = 2                                     #flashing line proximity in pixels
        c  = 5                                     #flashing corner border proximity  in pixels
        x1 = self.x1
        y1 = self.y1
        x2 = self.x2
        y2 = self.y2
        r = (x1,y1,x2,y2)
        #self.play = 0                            #stopping playback while modifying crop
        
        if x > x1-p and x < x1+p:
            if   y > y1-p and y < y1+p:
                self.set_object_left_top_corner()
                self.flash_object(r,[((x1-c,y1-c),(x1+c, y1+c))])
                return 'left_top_corner'         
            elif y > y2-p-1 and y < y2+p-1:
                self.set_object_left_bottom_corner()
                self.flash_object(r,[((x1-c,y2-c-1),(x1+c, y2+c-1))])
                return 'left_bottom_corner'           
            else:
                self.set_object_left_line()
                self.flash_object(r,[((x1-f,0),(x1+f, self.h))])
                return 'left_line'          
        elif x > x2-p-1 and x < x2+p-1:
            if y > y1-p-1 and y < y1+p-1:
                self.set_object_right_top_corner()
                self.flash_object(r,[((x2-c-1,y1-c),(x2+c-1, y1+c))])
                return 'right_top_corner'          
            elif y > y2-p-1 and y < y2+p-1:
                self.set_object_right_bottom_corner()
                self.flash_object(r,[((x2-c-1,y2-c-1),(x2+c-1, y2+c-1))])
                return 'right_bottom_corner'          
            else:
                self.set_object_right_line()
                self.flash_object(r,[((x2-f-1,0),(x2+f-1,self.h))])
                return 'right_line'          
        elif y > y1-p and y < y1+p:
            self.set_object_top_line()
            self.flash_object(r,[((0,y1-f),(self.w, y1+f))])
            return 'top_line'       
        elif y > y2-p-1 and y < y2+p-1:
            self.set_object_bottom_line()
            self.flash_object(r,[((0,y2-f-1),(self.w, y2+f-1))])
            return 'bottom_line'
        elif x > x1 and x < x2 and y > y1 and y < y2:
            self.set_object_all(x, y)
            self.flash_object(r,[((x1-f,y1-f),(x2+f-1, y2+f-1)),((x1+f,y1+f),(x2-f-1, y2-f-1))])
            return 'all'
        else:
            return None

            
    def set_object_left_top_corner(self,*_):
        self.xa, self.ya = self.x2, self.y2
            
    def set_object_left_bottom_corner(self,*_):
        self.xa, self.ya = self.x2, self.y1
        
    def set_object_left_line(self,*_):
        self.xa, self.ya = self.x2, self.y1
        self.useY = False
        
    def set_object_right_top_corner(self,*_):
        self.xa, self.ya = self.x1, self.y2
        
    def set_object_right_bottom_corner(self,*_):
        self.xa, self.ya = self.x1, self.y1
        
    def set_object_right_line(self,*_):
        self.xa, self.ya = self.x1, self.y1
        self.useY = False
        
    def set_object_top_line(self,*_):
        self.xa, self.ya = self.x2, self.y2
        self.useX = False
        
    def set_object_bottom_line(self,*_):
        self.xa, self.ya = self.x1, self.y1
        self.useX = False
        
    def set_object_all(self, x, y):
        self.xa, self.ya = self.x1,self.y1
        self.dx = x - self.x1
        self.dy = y - self.y1
        
    '''
    object_step_up()down, left and right  gets a step value, smallest by resolution mods and subsumpling mods,
    this is for a keyboard stepping only,it never gets here if using mouse
    '''
    def object_step_up(self):        
        if self.object == 'all': self.move_object(0, -self.mody_subs)
        else:                    self.move_object(0, -max(self.mody, self.mody_subs))
     
    def object_step_down(self):
        if self.object == 'all': self.move_object(0, self.mody_subs)
        else:                    self.move_object(0, max(self.mody, self.mody_subs))
        
    def object_step_left(self):
        if self.object == 'all': self.move_object(-self.modx_subs, 0)
        else:                    self.move_object(-max(self.modx, self.modx_subs), 0)                 
        
    def object_step_right(self):
        if self.object == 'all': self.move_object(self.modx_subs, 0)
        else:                    self.move_object(max(self.modx, self.modx_subs), 0)                 


    def move_object(self,x,y):              
        '''
        move_object() is for keyboard stepping to simulate mouse movement,
        it never gets here if using mouse,
        x,y is step increment for moving
        '''                                        
        if self.object is None:  return

        if   self.object == 'all':
            new_position   = (self.x1+x, self.y1+y)
            self.set_object_all(self.x1, self.y1)
        elif self.object == 'top_line':            new_position   = (self.x1+x, self.y1+y)
        elif self.object == 'bottom_line':         new_position   = (self.x2+x, self.y2+y)
        elif self.object == 'right_line':          new_position   = (self.x2+x, self.y2+y)
        elif self.object == 'right_bottom_corner': new_position   = (self.x2+x, self.y2+y)
        elif self.object == 'right_top_corner':    new_position   = (self.x2+x, self.y1+y)
        elif self.object == 'left_line':           new_position   = (self.x1+x, self.y1+y)
        elif self.object == 'left_bottom_corner':  new_position   = (self.x1+x, self.y2+y)
        elif self.object == 'left_top_corner':     new_position   = (self.x1+x, self.y1+y)
            
        if self.object == 'all':  rectangle = self.move_rectangle(*new_position)
        else:                     rectangle = self.new_rectangle(*new_position)
        self.live_crop_info(rectangle)
        if not self.play:
            cv2.imshow(self.title, self.img_and_selection(self.img, rectangle, self.color))
        getattr(self, f'set_object_{self.object}')(self.x1,self.y1)      #set object for another move if there is
                                           
        
    def flash_object(self, r, flash_rectangles):
        img = self.img_and_selection(self.img, r, self.color)
        for tuple_pair in flash_rectangles:
            cv2.rectangle(img, *tuple_pair, self.flash_color, 1, cv2.LINE_AA)
        cv2.imshow(self.title, img)
        
    def img_and_selection(self, img, r, c):
        x1,y1,x2,y2 = r
        final = cv2.bitwise_not(img)
        #crop = cv2.UMat(img, [y1, y2], [x1, x2]) #to do accelerating
        final[y1:y2, x1:x2] = img[y1:y2, x1:x2]
        cv2.line(final, (x1, 0), (x1, self.h), c, 1, cv2.LINE_AA)
        cv2.line(final, (0, y1), (self.w, y1), c, 1, cv2.LINE_AA)
        cv2.line(final, (max(x1,x2-1), 0), (max(x1,x2-1), self.h), c, 1, cv2.LINE_AA)
        cv2.line(final, (0, max(y1,y2-1)), (self.w, max(y1,y2-1)), c, 1, cv2.LINE_AA)
        return final

    def live_crop_info(self, r):
        x1,y1,x2,y2 = r
        self.print_info(self.cropping_line_text(x2-x1,y2-y1,*self.get_absolute_offsets(x1,y1)))
####                cv2.putText(dist, info, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 4)  #fontScale=0.4

        
    def trackbar_change(self, pos):
        self.frame = int(pos)
        if self.play == 0:
            self.show_frame()        

    def reset_preview(self):
        self.reset_preview()

    def build_window(self, title, mouseAction):
        if self.fullscreen:
            self.set_window_fullscreen(title)
        else:
            self.set_window_normal(title)
        cv2.setMouseCallback(title, mouseAction)
        
        
    def set_window_normal(self, title):
        try:
            cv2.namedWindow(title, cv2.WINDOW_NORMAL) #strict 1:1 cv2.WINDOW_AUTOSIZE | cv2.WINDOW_KEEPRATIO or flags=cv2.WINDOW_GUI_NORMAL
            cv2.setWindowProperty(title,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        except:
            self.print_info(self.print_clip_name() +': {} errors in normal screen resizing'.format(self.i+1))
            
    def set_window_fullscreen(self, title):
        try:
            cv2.namedWindow(title, cv2.WINDOW_KEEPRATIO) #cv2.WND_PROP_FULLSCREEN a bez aspect ratio radku
            cv2.setWindowProperty(title, cv2.WND_PROP_ASPECT_RATIO,cv2.WINDOW_KEEPRATIO)
            cv2.setWindowProperty(title, cv2.WND_PROP_FULLSCREEN,  cv2.WINDOW_FULLSCREEN)  
        except:
            self.print_info(self.print_clip_name() +': {} errors in full screen resizing'.format(self.i+1))
            
    def slider_switch(self):
        if self.slider:
            cv2.destroyWindow(self.title)                        #have to re-build window to get rid of slider
            self.build_window(self.title, self.mouseAction)         
        else:
            self.build_slider()
        self.slider = not self.slider
        
    def fullscreen_switch(self):
        if self.fullscreen:
            #set normal screen
            self.redraw_normal_screen(reset=False)
            cv2.resizeWindow(self.title, self.placement[2], self.placement[3])           
            cv2.moveWindow(self.title, self.placement[0], self.placement[1])
            #move correction, (cv2.moveWindow and cv2.getWindowImageRect() are off from each other)
            x,y,_,_ = cv2.getWindowImageRect(self.title)
            cv2.moveWindow(self.title, 2*self.placement[0] - x, 2*self.placement[1] - y)               
        else:
            #storing normal window position before going fullscreen
            self.placement = cv2.getWindowImageRect(self.title)
            self.redraw_fullscreen()
        
    def redraw_normal_screen(self, reset):
        self.fullscreen = False
        if self.slider:
            cv2.destroyWindow(self.title)                        #slider cannot be adjusted, so build all again
            self.build_window(self.title, self.mouseAction)
            if not reset:
                cv2.resizeWindow(self.title, self.placement[2], self.placement[3])
                cv2.moveWindow(self.title, self.placement[0], self.placement[1])
            else:
                cv2.resizeWindow(self.title, self.init_preview_width, self.init_preview_height )
                if not self.init_window_move():
                    cv2.moveWindow(self.title, self.placement[0], self.placement[1])
            self.build_slider()
        else:
            self.set_window_normal(self.title)
            if reset:
                cv2.resizeWindow(self.title, self.init_preview_width, self.init_preview_height )
                self.init_window_move()                
                                  
        #img = cv2.resize(img, (w, h), fx=1.0 / tilt, fy=1.0, interpolation=cv2.INTER_NEAREST)
                
    def init_window_move(self):
        x,y,_,_ = cv2.getWindowImageRect(self.title)
        if x < 0:                                              #if left, top corner is off monitor , move window
            cv2.moveWindow(self.title, self.position[0], y)
            return True
        return False
        
    def redraw_fullscreen(self):
        self.fullscreen = True
        if self.slider:
            cv2.destroyWindow(self.title)
            self.build_window(self.title, self.mouseAction)
            self.build_slider()
        else:
            self.set_window_fullscreen(self.title)

    def build_slider(self):
        cv2.createTrackbar('Frames', self.title, self.frame, self.frames[1]-1, self.trackbar_change)
        
    def print_statusBar(self,info):
        cv2.displayStatusBar(self.title, info)
        
    def print_info(self, info):
        try:
            if self.Qt:
                cv2.displayStatusBar(self.title, info)
        except:
            pass
        self.log(info)
        
    def zoom_out(self):
        self.crop_to_previous()

    def quick_2x_zoom_in(self, *mouse_position):
        '''
        quick zooms-in 2x, using mouse position as a center for zooming,
        basically it is just cropping getting half width and heinght and drawing it into the same window,
        it saves RAM and preview is faster
        '''
        try:
            x,y =  mouse_position
        except Exception:
            x,y = (self.ix,self.iy)
            
        #self.play = 0                  #stopping preview
            
        current_w = self.rgbs[self.i].width
        current_h = self.rgbs[self.i].height
        
        if x == -1:
            x,y = (current_w/2,current_h/2)
            
        #new width and height for cropping (half whatever window has now) and respecting mod
        w = int(current_w/2)
        w = w - w % self.modx
        h = int(current_h/2)
        h = h - h % self.mody
       
        #x1 and y1 are left top corner coordinates for crop 
        x = max(0, x - int(w/2) )  
        y = max(0, y - int(h/2) )
        x1 = x - x % self.modx_subs
        y1 = y - y % self.mody_subs
               
        #right bottom corner for crop, it is never used, it is just used to recalculate x1,y1
        #if that corner would end up off screen
        x2 = min(current_w, x1 + w)
        y2 = min(current_h, y1 + h)
        if x2 == current_w: x1 = current_w - w
        if y2 == current_h: y1 = current_h - h

        #absolute values for crop, class atributes
        self.x1, self.y1 = x1, y1
        self.x2 = self.x1 + w
        self.y2 = self.y1 + h
        self.width  = w
        self.height = h
        self.left, self.top = self.get_absolute_offsets(self.x1, self.y1)
        
        #cropping
        self.crop_to_new(self.width, self.height, self.left, self.top)

        
    def pixel_info(self):
        '''
        using self.ix and self.iy as current mouse coordinates from mouseAction()

        prints original clip's:
        clip index, pic. type, frame number, absolute pixel coordinates, original clip pixel values, and RGB preview pixel values
        '''
        if self.ix == -1:
            self.print_info(self.print_clip_name() +': {} mouse is off preview area'.format(self.i+1))
            return
        x = self.ix
        y = self.iy
        xa, ya = self.get_absolute_offsets(x, y)   #absolute pixel coordinates
        
        #original clip pixel values
        clip = self.clips_orig[self.i]
        p0, p1, p2 = self.get_pixel_values(clip, self.frame, xa,ya)
        
        pt=''
        try:
            pt = f'{clip.get_frame(self.frame).props["_PictType"].decode()}'
        except:
            pass        
        info = []
        info.append(f'clip{self.i+1}: {pt} Frame:{self.frame}  Pixel: {xa},{ya}   {clip.format.name} ')
        cf = clip.format.color_family
        if cf == vs.YUV or clip.format.name == 'CompatYUY2':
            info.append(f'y:{p0}  u:{p1}  v:{p2}')
            
        elif cf == vs.RGB or clip.format.name == 'CompatBGR32':
            info.append(f'r:{p0}  g:{p1}  b:{p2}')

        elif cf == vs.GRAY:
            info.append(f'y:{p0}')
         
        elif cf == vs.YCOCG:
            info.append(f'y:{p0}  Co:{p1}  Cg:{p2}')

        else:
            info.append(f'could not read source format, values: {p0}, {p1}, {p2}')
            
        #preview clip values      
        info.append('    preview: r:{2}  g:{1}  b:{0}'.format(*self.img[y][x]))  #tuple is returned from numpy array: (B,G,R)
        info = ''.join(info)
        self.log(info)
        if self.Qt:
            self.print_statusBar(info)
            
    def get_pixel_values(self, clip, frame, x,y):
        '''
        returns pixel values for pixel,
        p0,p1,p2 could be Y,U,V or R,G,B values
        '''
        try:
            fr = clip.get_frame(frame)
            planes =[fr.get_read_array(i) for i in range(clip.format.num_planes)]
        except:
            pass
        
        if clip.format.name == 'CompatYUY2':          #Interleaved COMPATYUY2, two pixels share U and V
            try:                                      #values seem to be in 2byte packs: YU,YV, ....
                pack = planes[0][y][x]
                p0 = pack & 0xFF
                p1 = (pack >> 8) & 0xFF
                if x % 2 == 0:                        #got YU pack
                    pack = planes[0][y][x+1]
                    p2 = (pack >> 8) & 0xFF
                else:                                 #got YV pack
                    p2 = p1
                    pack = planes[0][y][x-1]
                    p1 = (pack >> 8) & 0xFF                                
            except:
                p0, p1, p2 = ('x','x','x')               
            
        elif clip.format.name == 'CompatBGR32':             #Interleaved COMPATBGR32, 1 pixel = BGRA = 4byte pack
            try:
                pack = planes[0][clip.height-1 - y][x]      #COMPATBGR32 is vertically flipped 
                p2 = pack & 0xFF
                p1 = (pack >> 8) & 0xFF
                p0 = (pack >> 16) & 0xFF
                #pA = (pack >> 24) & 0xFF  #alpha in CompatBGR32, did not went into this yet, if vs can store it in there or how
            except:
                p0, p1, p2 = ('x','x','x')
            
        else:                                            #Planar videos
            try:    p0 = planes[0][y][x]
            except: p0 = 'x'
            ys = y >> clip.format.subsampling_h          #chroma planes are reduced if subsampling
            xs = x >> clip.format.subsampling_w
            try:    p1 = planes[1][ys,xs]
            except: p1 = 'x'            
            try:    p2 = planes[2][ys,xs]
            except: p2 = 'x'
            
        return p0,p1,p2    
        
       
    def left_arrow(self):
        self.frame -=  1
        
    def end(self):
        self.frame = self.frames[1]-1
        
    def right_arrow(self):
        self.frame += 1

        
    def home(self):
        self.frame = 0
        
    def write_image(self):
        #if self.play: return  #no writing during playback
        if self.img_dir and not os.path.isdir(self.img_dir):
            self.log('not a valid path: ', self.img_dir)
            return
        img_path = os.path.join(self.img_dir, self.print_clip_name() +'_{:02}_{}_frame_{:07}.png'.format(self.i+1,self.previewData[-1],self.frame))
        '''
        self.img is numpy data and up-scaled by openCV to fit whatever window,
        it needs to be upscaled for real writing otherwise print would be just real clip resolution (1:1, smaller).
        '''
        _,_,w,h = cv2.getWindowImageRect(self.title)
        resized = cv2.resize(self.img, (w, h), interpolation = cv2.INTER_NEAREST)
        cv2.imwrite(img_path, resized)
        self.print_info(self.print_clip_name() +': {}  writing image: {}'.format(self.i,img_path))        

    ''' cv2.resize interpolation:
    INTER_NEAREST - a nearest-neighbor interpolation
    INTER_LINEAR - a bilinear interpolation (used by default)
    INTER_AREA - resampling using pixel area relation. It may be a preferred method for image decimation, as it gives moire’-free results.
                 But when the image is zoomed, it is similar to the INTER_NEAREST method.
    INTER_CUBIC - a bicubic interpolation over 4x4 pixel neighborhood
    INTER_LANCZOS4 - a Lanczos interpolation over 8x8 pixel neighborhood
    '''
    
    def write_image_1_to_1(self):
        #if self.play: return  #no writing during playback
        if self.img_dir and not os.path.isdir(self.img_dir):
            self.log('not a valid path: ', self.img_dir)
            return
        img_path = os.path.join(self.img_dir, self.print_clip_name() +'_{:02}__1;1_{}_frame_{:07}.png'.format(self.i+1,self.previewData[-1],self.frame))
        cv2.imwrite(img_path, self.img)
        self.print_info(self.print_clip_name() +': {}  writing image: {}'.format(self.i,img_path))
        
    def help(self):
        self.log(HOTKEYS_HELP)
        
    
    def closing(self):
        self.close = True
    
            
    def validate_clips(self):
        '''
        clips must be single vs.VideoNode or list of vs.VideoNodes
        '''
        self.resolutions = []
        if isinstance(self.clips_orig, vs.VideoNode):
            self.clips_orig = [self.clips_orig]
        elif isinstance(self.clips_orig, list):
            for clip in self.clips_orig:
                if not isinstance(clip, vs.VideoNode):
                    raise ValueError("[Preview] Input needs to be a clip or list of clips!")
                self.resolutions.append((clip.width, clip.height)) 
        else:
            raise ValueError("[Preview] Input needs to be a clip or list of clips")      
        if len(self.clips_orig)>9:
            self.log("more than 9 clips")


  
    def validate_frames(self):
        '''
        default is the whole clip length, if not specified
        '''
        if isinstance(self.frames, vs.VideoNode):      #clip loaded as frames argument
            raise TypeError("[Preview] clip arguments must be enclosed in a list, example: Preview([clip1,clip2])")
        
        if self.frames is None:
            self.frames = [0,len(self.clips_orig[0])]
        try:
            s = self.frames[0]
            e = self.frames[1]-1
            self.clips_orig[0][s]
            self.clips_orig[0][e]            
        except:            
            self.log("wrong 'frames', must be a list of two integers within clip's range")
            self.log("defaulting to frames = [0,{}]".format(len(self.clips_orig[0])))
            self.frames = [0,len(self.clips_orig[0])]      
        
        
    def validate_delay(self):
        if self.delay is None:
            self.delay = self.clips_orig[0].fps_den/self.clips_orig[0].fps_num 

        else:
            try:
                self.delay = self.delay/1000
            except:
                raise TypeError(f"[Preview] wrong delay: {self.delay} , it has to be an integer, miliseconds between frames")
        self.delay = abs(self.delay)

        
    def validate_img_dir(self):
        if self.img_dir is None:
            self.img_dir = os.path.dirname(os.path.abspath(__file__))

        if self.img_dir and not os.path.isdir(self.img_dir):
            raise ValueError('[Preview] not a valid directory path: ',  self.img_dir)
    
    def validate_matrix(self):
        '''
        Has to be same matrix_in_s string value as used in Vapoursynths scripts.
        If more clips are loaded, this would override all of them,
        so you'd rather specify matrix_in_s in Vapoursynth script, not here,  if color space is not the same for clips.
        '''
        if self.matrix_in_s and not self.matrix_in_s in Conversions.MATRIX_USABLE.values():
            self.log(f"\nWarning, matrix_in_s  argument: '{self.matrix_in_s}', is not usable")
            self.log("usable values:\n{}\n".format([x for x in Conversions.MATRIX_USABLE.values()]))
            self.matrix_in_s = None

            
    def validate_kernel(self):
        try:
            getattr(vs.core.resize, self.kernel)
        except:
            raise ValueError(f"[Preview] wrong kernel argument: '{self.kernel}', valid resize arguments:\n'Point','Bicubic','Lanczos','Spline16','Spline36'")

            
    def validate_position(self):
        '''
        left, top corner of Preview window
        needs to be tuple or list with two integers
        '''
        if isinstance(self.position, tuple) or isinstance(self.position, list):
            if not isinstance(self.position[0], int) or not isinstance(self.position[1], int):
                raise ValueError('[Preview] position argument for Preview window must be tuple with two integers, example: position=(60,60)')
                
        else:
            raise ValueError("[Preview] 'position' argument for Preview window must be tuple, example: position=(60,60)")

        
    def validate_preview_dimensions(self):
        '''
        preview window dimensions in pixels on screen, not video resolution,
        clips do not get resized
        if None, self.clips_orig[0].width and self.clips_orig[0].height are used, real first clip width and height
        '''
        for string in ['width', 'height']:
            var = getattr(self, 'init_preview_' + string)
            if var is None:
                setattr(self, 'init_preview_' + string, getattr(self.clips_orig[0], string))
            else:
                if not (isinstance(var, int) and var > 1 and var <=20000):
                    raise ValueError(f"[Preview] 'preview_{string}' argument must be positive integer and less than 20000")
            
        
    def validate_mod(self, modx, mody):
        '''
        if mods are not specified, defaults are: modx=2 and mody=2
        then subsumpling is being checked and mod could be adjusted because
        this must be True, otherwise crop in Vapoursynth might fail with real YUV clips:
        modx >= (1 << clip.format.subsampling_w)
        mody >= (1 << clip.format.subsampling_y) 

        and get maximum subsumplings for all clips, mod_x_subs, mod_y_subs
        because first point for crop must follow subsampling, not modx or mody

        maximum values of subsumpling and mods or are used for crop, unless, ignore_subsumpling=True, modx=1, mod_y=1 for example,
        this would crop to any size and ignoring subsumpling. If as a result crop would fail in real Vapoursynth,
        it gives a message while printing crop line though: #fails with original YUV!
        '''
        
        self.log('[Preview.validate_mod]')
        if not isinstance(modx, int):
            raise TypeError(f"[Preview] wrong 'mod_x' argument: {mod_x}, it has to be an integer, usual values are 2,4,8 or 16")
        if not isinstance(mody, int):
            raise TypeError(f"[Preview] wrong 'mod_y' argument: {mod_y}, it has to be an integer, usual values are 2,4,8 or 16")
        modx=abs(modx)
        mody=abs(mody)
        old_modx = modx
        old_mody = mody
        s_w_max = 1
        s_h_max = 1
        modx_subs, mody_subs = (1,1)
        self.log(f'video resolution mod_x={modx}')
        self.log(f'video resolution mod_y={mody}')
        respect_x_subs = RESPECT_X_SUBSAMPLING
        respect_y_subs = RESPECT_Y_SUBSAMPLING
        self.log(f'global RESPECT_X_SUBSAMPLING is {RESPECT_X_SUBSAMPLING}')
        self.log(f'global RESPECT_Y_SUBSAMPLING is {RESPECT_Y_SUBSAMPLING}')
        if self.ignore_subsampling:
            respect_x_subs = False
            respect_y_subs = False
        self.log('subsampling_w, subsampling_h for clips:')            
        for i , is_error in enumerate(self.rgbs_error):
            if is_error:
                self.log(f'  clip{i+1}:          loaded with error')
            else:
                s_w = 1 << self.clips_orig[i].format.subsampling_w
                s_w_max = max(s_w_max, s_w)
                if respect_x_subs:
                    modx =      max(modx,      s_w)
                    modx_subs = max(modx_subs, s_w)
                s_h = 1 << self.clips_orig[i].format.subsampling_h
                s_h_max = max(s_h_max, s_h)
                if respect_y_subs:
                    mody =      max(mody,      s_h)
                    mody_subs = max(mody_subs, s_h)
                self.log(f'  clip{i+1}:  {s_w}, {s_h}    {self.clips_orig[i].format.name}')
        if self.ignore_subsampling:
            self.log('ignore_subsampling=True (both x and y)')
            if not (s_w_max == 1 and s_h_max == 1):
                self.log('  user overriding global settings to also select points within subsampling'
                         '\n  which gives error if using that cropping line in vapoursynth')
            else:
                self.log('  no loaded clip has subsampling anyway')
        else:
            self.log('ignore_subsampling=False')
        self.log('script evaluation for crop selection:')           
        if respect_x_subs and respect_y_subs:         
            if modx != old_modx: self.log(f'  mod_x={modx},  that is correction of  mod_x={old_modx}, cannot be less than subsampling')
            if mody != old_mody: self.log(f'  mod_y={mody},  that is correction of  mod_y={old_mody}, cannot be less than subsampling')
            
        elif not respect_x_subs and respect_y_subs:
            modx_subs = 1
            if mody != old_mody: self.log(f'  mod_y={mody},  that is correction of  mod_y={old_mody}, cannot be less than subsampling')
            
        elif respect_x_subs and not respect_y_subs:
            mody_subs = 1
            if modx != old_modx: self.log(f'  mod_x={modx},  that is correction of  mod_x={old_modx}, because it must be >= {modx}')                  
            
        elif not respect_x_subs and not respect_y_subs:
            modx_subs, mody_subs = 1, 1
            
        self.log(f'  subsampling mods:      {modx_subs}, {mody_subs}   while selecting crop area, first selected point snaps to those mods')                
        self.log(f'  video resolution mods: {modx}, {mody}   while drawing crop area, width and height are snapping to those mods')

        return modx, mody, modx_subs, mody_subs
    
        
    def validate_boolean(self, dictionary):
        for key, value in dictionary.items():
            if not isinstance(value, bool):
                raise TypeError(f"[Preview] wrong '{key}' argument: '{value}', it has to be boolean: True or False")            

            
    def limit_cache(self, given_cache, avail):
        if avail >= given_cache:
            return given_cache      
        deduc = 0
        if avail < 200:
            deduc = 50                   
            self.log('almost no RAM, preview and system likely to freeze'.format(avail))
            
        elif avail >=200 and avail < 400:
            deduc = 100                   
            self.log('not much RAM at all, freezing likely, lagish preview'.format(avail))
            
        elif avail >= 400 and avail < 1024:
            deduc = 200
            self.log('more RAM would give better performance'.format(avail))
            
        elif avail >= 1024 and avail < 1536:
            deduc = 380 
                        
        else:
            deduc = 450
            
        new_cache =  avail - deduc
        return new_cache if new_cache < given_cache else given_cache


    def crop_to_previous(self):    
        '''
        zoom-out when 'Esc' is pressed
        previous index data from self.previewData are used to set proper core.std.cropAbs() from original clip'''
        
        if len(self.previewData) == 1:  #fully zoomed out already
            return
        
        width, height, left, top = self.previewData[-2]

        try:              
            for i, rgb in enumerate(self.rgbs_orig):
                self.rgbs[i] = core.std.CropAbs(rgb, width, height, left, top)
        except:
            self.log(f'{self.print_clip_name()}: {self.i+1} preview return failed')    

        else:
            if self.isCropping:
                '''update selection values from previous crop to become current crop'''
                x_abs,y_abs = self.get_absolute_offsets(self.x1, self.y1)
                self.x1 = x_abs - self.previewData[-2][2]
                self.y1 = y_abs - self.previewData[-2][3]
                self.x2 = self.x1 + self.width
                self.y2 = self.y1 + self.height
                self.w  = self.rgbs[self.i].width
                self.h  = self.rgbs[self.i].height
                del self.previewData[-1]
                self.print_info(self.cropping_line_text(self.width, self.height, x_abs,y_abs))
            else:
                del self.previewData[-1]
                self.print_info(self.cropping_line_text(width, height, left, top))
                self.width, self.height, self.left, self.top = width, height, left, top
            
            
            #self.redraw_window()
            
    def crop_to_new(self,width, height, left, top):
        '''
        zoom in or crop
        crop preview to new width and height and store data into self.previewData
        '''
        
        try:          
            for i, rgb in enumerate(self.rgbs_orig):
                self.rgbs[i] = core.std.CropAbs(rgb, width, height, left, top)
        except:
            self.log(f'{self.print_clip_name()}: {self.i+1} preview return failed')    

        else:
            self.previewData.append([width,height,left,top])
            self.print_info(self.cropping_line_text(width, height, left, top))

      
    def reset_preview(self):
        try:
            for i, rgb in enumerate(self.rgbs_orig):
                self.rgbs[i] = rgb
        except:
            self.log(f'clip: {self.i+1} preview reset failed in clip or one of clips')
        else:
            self.isCropping = False
            self.redraw_window()
            self.previewData_reset()
            self.print_info(self.cropping_line_text(*self.previewData[0]))

            
    def previewData_reset(self):
        '''
        creating first list index as original rgb data: width, height, left, top
        '''
        self.previewData = [[self.rgbs_orig[0].width, self.rgbs_orig[0].height , 0, 0]]
                    
    def redraw_window(self):
        '''
        avoiding this redraw_window() actually keeps original window size after crop or zoom,
        if calling this function, window gets redrawn to 1:1 after crop or zoom, so window gets smaller
        '''
        self.placement = cv2.getWindowImageRect(self.title)
        if self.fullscreen:
            self.redraw_fullscreen()
        else:
            self.redraw_normal_screen(reset=True)
        

    def get_absolute_offsets(self, relative_x , relative_y):
        '''
        absolute current offsets are stored in self.previewData,
        [-1] means last index in list,
        current self.left and self.top are third and forth index so using [2] and [3]
        '''
        return self.previewData[-1][2] + relative_x,  self.previewData[-1][3] + relative_y

    
    def cropping_line_text(self, w,h,l,t):
        s_w = 1 << self.clips_orig[self.i].format.subsampling_w
        s_h = 1 << self.clips_orig[self.i].format.subsampling_h
        if w % s_w == 0 and  h % s_h == 0  and l % s_w == 0 and t % s_h == 0 and w != 0 and h != 0:
            check = ''
            self.color = self.good_c
        else:
            check = ' #fails in vs'
            self.color = self.bad_c
        info = (f'{self.print_clip_name()}{self.i+1} = '
                f'core.std.CropAbs(clip{self.i+1}, width={w}, height={h}, left={l}, top={t}) ')
        if len(self.previewData) > 1 or self.isCropping:
             info += f'#mods({self.modx},{self.mody}) #subs({self.modx_subs},{self.mody_subs}){check}'
        return info
    
    def print_clip_name(self):
        if self.isCropping:
             return 'selection_in_clip'
        
        if len(self.previewData) >1:
            return 'cropped_clip'
        else:
            return 'clip'

    def freeRAM(self):
        '''
        getting free RAM
        first it uses non standard library cross platform psutil
        if modul is not installed, it falls back using Linux or Windows ways to get free RAM
        so for Mac it needs psutil: to install psutil: pip3 psutil install
        '''

        avail = None
        
        #cross platform try if psutil is installed
        try:
             mem = pstutil.virtual_memory()
             avail = int(mem.available/1024/1024)
             if avail and isinstance(avail, int):
                 return avail
        except:
            pass
                   
        #linux fallback
        try:
            meminfo = dict((i.split()[0].rstrip(':'),int(i.split()[1])) for i in open('/proc/meminfo').readlines())
            avail = int(meminfo['MemAvailable']/1024)
            if avail and isinstance(avail, int):
                return avail 
        except:
            pass
                
        #windows fallback
        try:
            proc = os.popen('wmic.exe OS get FreePhysicalMemory')
            l = proc.readlines()   #l should be a list
            proc.close()
        except:
            pass

        else:
            for i, item in enumerate(l):
                try:
                    avail = int(l[i])
                    avail = int(avail/1024)
                    if avail and isinstance(avail, int):
                        return avail 
                except:
                    pass
                
        #failed to get free RAM            
        self.log("[freeRAM] Install psutil(pip3 psutil install) to get free RAM for limiting cache")
        self.log("[freeRAM] psutil is needed to get free RAM on Mac") #or add some fallback code for Mac here that works        
    
class Conversions:
    
    MATRIX_USABLE = {
                  1 : '709'   ,
                  4 : 'fcc'   ,
                  5 : '470bg' ,
                  6 : '170m'  ,
                  7 : '240m'  ,
                  8 : 'ycgco' ,
                  9 : '2020ncl'  ,
                 10 : '2020cl'   ,
                 12 : 'chromancl',
                 13 : 'chromacl ',
                 14 : 'ictcp'    }  
    
    def getMatrix(self, clip=None, matrix_in_s=None):
        '''
        lots of logging,  so its a bit wild with ifs,
        wanted to make clear and print what actually happens, why matrix was selected as such etc...
        '''
        matrix_in = None
        log = ''    
        if not isinstance(clip, vs.VideoNode):
            log = "[getMatrix] input needs to be a clip"
            return None, matrix_in_s, log
        
        if clip.format.color_family != vs.YUV:
            return matrix_in, matrix_in_s, log
         
        if matrix_in_s: 
            if matrix_in_s not in self.MATRIX_USABLE.values():
                log = "[getMatrix] input argument {} is not usable as matrix_in_s\n".format(matrix_in_s)
                matrix_in_s = None
            else:
                log = "[getMatrix] matrix_in_s argument override, matrix_in_s = '{}'\n".format(matrix_in_s)
                return matrix_in, matrix_in_s, log
            
        else:
            try:
                matrix_in = clip.get_frame(0).props['_Matrix']
            except:
                log = "[getMatrix] _Matrix NOT found in props\n"
            if matrix_in:
                try:
                    matrix_in_s = self.MATRIX_USABLE[matrix_in]
                    if matrix_in_s not in self.MATRIX_USABLE.values():
                        matrix_in_s = None
                        log = "[getMatrix] _Matrix={} is not usable\n".format(matrix_in)
                except:
                    matrix_in_s = None
                    log = "[getMatrix] _Matrix={} is not usable\n".format(matrix_in)
                
        if matrix_in_s:
            log = "[getMatrix] _Matrix={0}, using matrix_in={0}/matrix_in_s = '{1}'\n".format(matrix_in, matrix_in_s )
        else:
            if   clip.width <= 1024 and clip.height <= 480: matrix_in, matrix_in_s = (6, '170m')
            elif clip.width <= 1024 and clip.height <= 576: matrix_in, matrix_in_s = (5, '470bg')
            else: matrix_in, matrix_in_s = (1, '709')
            log += "[getMatrix] defaulting, which could be wrong, to matrix_in_s = '{}'\n".format(matrix_in_s)
                
        return matrix_in, matrix_in_s, log
            
   
    def toRGB(self, clip=None, matrix_in_s=None, depth=None, kernel=None, sample_type=None):
        '''
        yuv to rgb conversion
        there are bunch of YUV  to RGB scripts out there, but needed to make my own so it prints what it actually does,
        if it defaults to matrix or not , prints actual conversion line etc...

        returns rgb clip and log, 
        returns None and log, if conversion fails,
        defaults:  input is limited range, RGB full range, and output is full RGB range

        matrix_in_s, same as in Vapoursynth
        kernel, same as Vapoursynth attribute values
        
        sample type is only relevant with 16bit, otherwise is ignored, less than 16bit must be INTEGER and 32 is FLOAT 
        sample_type  = None   , same as input clip
                     = 0 or  vs.INTEGER
                     = 1 or  vs.FLOAT
        depth = None        converts all clips into RGB with the same bit depth as original,
                            if that bit depth is not pre-registered (like 8,9,10,16 are), rgb depth will be registered (11,12,13,14,15),
                            if clip is 32bit floating point, it will convert to RGBS 32bit floating point
                            
        depth = 8,9,10,11,12,13,14,15,16 or 32  #same as None, except bit depth is given, not taking it from original clip
        '''
        
        if not isinstance(clip, vs.VideoNode):
            return None, '[toRGB] input needs to be a vapoursynth VideoNode/clip'
        
        log=''
        
        #bitdepth
        depth_in = clip.format.bits_per_sample
        if not depth:
            depth = depth_in
        else:
            if not isinstance(depth, int) or depth < 8 or (depth > 16 and depth != 32):
                depth = depth_in
                log += '[toRGB] depth must be integer from 8 to 16 range or 32'
                log += '[toRGB] defaulting to clips bit depth: {}bit\n'.format(depth_in)                
        
        #sample_type output       
        if sample_type   == 0: sample_out = vs.INTEGER
        elif sample_type == 1: sample_out = vs.FLOAT
        elif not sample_type:
            sample_out = clip.format.sample_type            
        else:
            #sample type was defined wrong
            if depth == 16:
                if clip.format.sample_type == vs.FLOAT:
                      string = 'vs.FLOAT' 
                else: string = 'vs.INTEGER'    
                log += '[toRGB] wrong sample type argument, using {}, same as the clip for 16bit output\n'.format(string)
                sample_out = clip.format.sample_type
            elif depth == 32:
                sample_out = vs.FLOAT
                log += '[toRGB] sample type arg ignored, must be vs.FLOAT for 32bit\n'
            else:
                sample_out = vs.INTEGER
                log += '[toRGB] sample type arg ignored, must be vs.INTEGER for less than 16bit output\n'
        #sample_type correction
        if depth < 16 and sample_out == vs.FLOAT:
            sample_out = vs.INTEGER
            log += '[toRGB] wrong sample type argument, using vs.INTEGER for less than 16bit\n'
        if depth == 32 and sample_out == vs.INTEGER:
            sample_out = vs.FLOAT
            log += '[toRGB] wrong sample type argument, only vs.FLOAT for 32 bit\n'        
                    
        #RGB output in string for getattr()
        RGBattr = f'RGB{depth*3}'
        try:
            getattr(vs, RGBattr)
        except:
            if depth != 32:
                setattr(vs, RGBattr, core.register_format(vs.ColorFamily.RGB, vs.INTEGER, depth, 0, 0).id)
                log += '[toRGB] setting new vapoursynth attribute {}\n'.format(RGBattr)
        if depth == 32:
            RGBattr = 'RGBS'
        if depth == 16 and sample_out==vs.FLOAT:
            RGBattr = 'RGBH'
   
        #resize kernel
        if kernel == None:
            log += "[toRGB] Defaulting to:  kernel = 'Bicubic'\n"
            kernel = 'Bicubic'
        else:
            try:
                getattr(vs.core.resize, kernel)
            except:
                log += "[toRGB] Wrong kernel, '{}', defaulting to:  kernel = 'Bicubic'\n".format(kernel)
                kernel = 'Bicubic'

        #matrix_in_s   
        if clip.format.color_family == vs.YUV:              
            matrix_in, matrix_in_s, matrix_log = self.getMatrix(clip, matrix_in_s)
            log = log + matrix_log
            
        else: matrix_in_s = None

        #attributes needed for conversion
        _resize    = getattr(vs.core.resize, kernel)
        format_out = dict(format = getattr(vs, RGBattr))
        
        #variables for printing and logging ,otherwise they have no purpose in conversion
        name = clip.format.name
        if matrix_in_s: inMatrix = "matrix_in_s = '{}',".format(matrix_in_s)
        else:           inMatrix = ''
        if clip.format.sample_type   == 0: inSample = 'INTEGER'
        elif clip.format.sample_type == 1: inSample = 'FLOAT'
        if sample_out == vs.INTEGER     : outSample = 'vs.INTEGER'
        else:                             outSample = 'vs.FLOAT'
        
        #zimg conversion
        try:
            log += '[toRGB] zimg conversion, {}bit {} {} to {}bit {} RGB:\n'.format(depth_in, inSample, name, depth, outSample)
            if matrix_in_s : clip = _resize(clip, **format_out, matrix_in_s = matrix_in_s)
            else:            clip = _resize(clip, **format_out)
            log += "[toRGB] vs.core.resize.{}(clip, {} format = vs.{})\n".format(kernel, inMatrix, RGBattr)            
        except:
            log += log_err()
            log += '[toRGB] conversion failed'
            return None, log
        
        return clip, log

        
                
if __name__ == '__main__':

    file='video.mp4'
    clip = core.ffms2.Source(file)
    Preview([clip])
