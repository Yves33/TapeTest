##############################################################################
## Tapetest options. time units in seconds
X_SCALE_WIDTH=10                            ## scale of x axis
DEBOUNCE=0.01                               ## key debounce delay. on windows, you may need to increase this delay (0.05 - 0.1) 
TIMEOUT=10*60                               ## timeout to stop recordings
LINEWIDTH=30                                ## line width
RIGHTCOLOR='g'                              ## green is fantastic!
LEFTCOLOR='r'                               ## red is even nicer!
FILENAMETEMPLATE='mouse_xx_wt_wt_{date}'    ## {date} will be replaced by current date & time
## key bindings. some people may use qwerty keyboards or something else
KEYLEFT='a'
KEYRIGHT='p'
KEYSTART=' '
KEYSAVE='s'
KEYZOOMIN='+'
KEYZOOMOUT='-'
## video recordings options
CAMERA=-1                                    ## which camera to use. use any negative number to disable synchronous video recordings
RESOLUTION=(640,480)                        ## camera resolution. The software will not check if resolution is supported!
VIDFOURCC='avc1'                            ## video codec for video compression
VIDCONTAINER='.mts'                         ## video container for video storage