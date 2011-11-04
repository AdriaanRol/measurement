unit pq_tttr_functions;

//{$DEFINE HH400}
{$DEFINE PH300}

// todo: - conditioning with sweeps
//       - check overflow timing

interface

type
  Pshort = ^word;
  Plong = ^longword;

  section_type = record            // data record defining a measurement section
    event_type: integer;           // event to be counted within a section
                                   // event definitions: see constants
    bin_size: integer;             // time resolution
                                   // (base resolution * 2^binsize),
                                   // Picoharp: base resolution 4 ps
                                   // Hydraharp: base resolution 1 ps
    offset: integer;               // offset of event counting with respect to
                                   // detection of 'section increment event'
                                   // (in units of binsize)
    duration: integer;             // duration of data acquisition
                                   // (in units of binsize)
    mode: integer;                 // mode of data acquisition: number of events
                                   // as function of time, repetition
                                   // and/or sweep index
                                   // (definitions: see constants)
    threshold_min: integer;        // only sections >= treshold_min are valid
    threshold_max: integer;        // only sections <= treshold_max are valid
    threshold_mode: integer;       // defines which threshold(s) to use
                                   // (definitions: see constants)
    reset_mode: integer;           // event to start over current section
                                   // (in conditional mode, without saving
                                   // previous data from this section)
                                   // (definitions: see constants)
    data: Plong;                   // data array for this section (1-, 2- or 3D)
    temp_data: array of integer;   // temporary data (only used in conditional
                                   // mode, before it is decided if this
                                   // sequence fullfills all thresholds)
    counts: integer;               // temporary event counts (only used in
                                   // conditional mode, before it is decided if
                                   // this sequence fullfills all thresholds)
  end;

procedure set_dev(dev_idx: integer); export; stdcall; // set device index

procedure set_abort_condition(event: integer); export; stdcall;

procedure set_debuglevel(level: integer); export; stdcall;

function start(Tacq: integer): integer; export; stdcall; // start data
                                                         // acquisition

function clear_sections(): integer; export; stdcall; // clear sections
                                                     // definitions

function add_section(                     // add new measurement section
  event_type: integer;
  bin_size: Integer;
  offset: Integer;
  duration: Integer;
  mode: Integer;
  threshold_min: Integer;
  threshold_max: Integer;
  threshold_mode:Integer;
  reset_mode:Integer;
  data:Plong): integer; export; stdcall;

function TTTR2_universal_measurement_speedmode_unconditional(
  sweeps: integer;         // number of sweep values
  repetitions: integer;    // number of repetitions
  sweep_inc_cond: integer; // condition for sweep increment
  sweep_res_cond: integer; // condition for sweep reset
  rep_inc_cond: integer;   // condition for repetition increment
  rep_res_cond: integer;   // condition for repetition reset
  sec_inc_cond: integer;   // condition for section increment
  seq_res_cond: integer;   // condition for sequence reset
  loop_order: integer;     // 0: repeat sweeps
                           // 1: sweep repetitions
  statistics: Plong        // data on statistics to return to python
  ): integer; export; stdcall;

function TTTR2_universal_measurement(
  sweeps: integer;         // number of sweep steps
  repetitions: integer;    // number of repetitions
  sweep_inc_cond: integer; // condition for sweep increment
  sweep_res_cond: integer; // condition for sweep reset
  rep_inc_cond: integer;   // condition for repetition increment
  rep_res_cond: integer;   // condition for repetition reset
  sec_inc_cond: integer;   // condition for section increment
  seq_res_cond: integer;   // condition for sequence reset
  loop_order: integer;     // 0: repeat sweeps
                           // 1: sweep repetitions
  statistics: Plong        // data on statistics to return to python
  ): integer; export; stdcall;

implementation

uses
  SysUtils;

const
  {$IFDEF HH400}
  {constants taken from HHDEFIN.H and ERRCODES.H}
  LIB_VERSION    =      '1.2';

  MAXDEVNUM      =          8;               // max num of USB devices
  HHMAXCHAN      =          8;               // max num of logical channels

  MAXBINSTEPS    =         12;
  MAXHISTLEN     =      65536;   // max number of histogram bins
  MAXLENCODE     =          6;   // max length code

  TTREADMAX      =     131072;   // 128K event records can be read in one chunk

  MODE_HIST      =          0;
  MODE_T2        =          2;
  MODE_T3        =          3;

  FLAG_OVERFLOW  =      $0001;   // histo mode only
  FLAG_FIFOFULL  =      $0002;
  FLAG_SYNC_LOST =      $0004;
  FLAG_REF_LOST  =      $0008;
  FLAG_SYSERROR  =      $0010;

  SYNCDIVMIN     =          1;
  SYNCDIVMAX     =         16;

  ZCMIN          =          0;   // mV
  ZCMAX          =         40;   // mV
  DISCRMIN       =          0;   // mV
  DISCRMAX       =       1000;   // mV

  CHANOFFSMIN    =     -99999;   // ps
  CHANOFFSMAX    =      99999;   // ps

  OFFSETMIN      =          0;   // ps
  OFFSETMAX      =     500000;   // ps
  ACQTMIN        =          1;   // ms
  ACQTMAX        =  360000000;   // ms  (100*60*60*1000ms = 100h)

  STOPCNTMIN     =          1;
  STOPCNTMAX     = 4294967295;   // 32 bit is mem max

  HH_ERROR_NONE                     =   0;

  HH_ERROR_DEVICE_OPEN_FAIL         =  -1;
  HH_ERROR_DEVICE_BUSY              =  -2;
  HH_ERROR_DEVICE_HEVENT_FAIL       =  -3;
  HH_ERROR_DEVICE_CALLBSET_FAIL     =  -4;
  HH_ERROR_DEVICE_BARMAP_FAIL       =  -5;
  HH_ERROR_DEVICE_CLOSE_FAIL        =  -6;
  HH_ERROR_DEVICE_RESET_FAIL        =  -7;
  HH_ERROR_DEVICE_GETVERSION_FAIL   =  -8;
  HH_ERROR_DEVICE_VERSION_MISMATCH  =  -9;
  HH_ERROR_DEVICE_NOT_OPEN          = -10;

  HH_ERROR_INSTANCE_RUNNING         = -16;
  HH_ERROR_INVALID_ARGUMENT         = -17;
  HH_ERROR_INVALID_MODE             = -18;
  HH_ERROR_INVALID_OPTION           = -19;
  HH_ERROR_INVALID_MEMORY           = -20;
  HH_ERROR_INVALID_RDATA            = -21;
  HH_ERROR_NOT_INITIALIZED          = -22;
  HH_ERROR_NOT_CALIBRATED           = -23;
  HH_ERROR_DMA_FAIL                 = -24;
  HH_ERROR_XTDEVICE_FAIL            = -25;
  HH_ERROR_FPGACONF_FAIL            = -26;
  HH_ERROR_IFCONF_FAIL              = -27;
  HH_ERROR_FIFORESET_FAIL           = -28;

  HH_ERROR_USB_GETDRIVERVER_FAIL    = -32;
  HH_ERROR_USB_DRIVERVER_MISMATCH   = -33;
  HH_ERROR_USB_GETIFINFO_FAIL       = -34;
  HH_ERROR_USB_HISPEED_FAIL         = -35;
  HH_ERROR_USB_VCMD_FAIL            = -36;
  HH_ERROR_USB_BULKRD_FAIL          = -37;

  HH_ERROR_LANEUP_TIMEOUT           = -40;
  HH_ERROR_DONEALL_TIMEOUT          = -41;
  HH_ERROR_MODACK_TIMEOUT           = -42;
  HH_ERROR_MACTIVE_TIMEOUT          = -43;
  HH_ERROR_MEMCLEAR_FAIL            = -44;
  HH_ERROR_MEMTEST_FAIL             = -45;
  HH_ERROR_CALIB_FAIL               = -46;
  HH_ERROR_REFSEL_FAIL              = -47;
  HH_ERROR_STATUS_FAIL              = -48;
  HH_ERROR_MODNUM_FAIL              = -49;
  HH_ERROR_DIGMUX_FAIL              = -50;
  HH_ERROR_MODMUX_FAIL              = -51;
  HH_ERROR_MODFWPCB_MISMATCH        = -52;
  HH_ERROR_MODFWVER_MISMATCH        = -53;
  HH_ERROR_MODPROPERTY_MISMATCH     = -54;

  HH_ERROR_EEPROM_F01               = -64;
  HH_ERROR_EEPROM_F02               = -65;
  HH_ERROR_EEPROM_F03               = -66;
  HH_ERROR_EEPROM_F04               = -67;
  HH_ERROR_EEPROM_F05               = -68;
  HH_ERROR_EEPROM_F06               = -69;
  HH_ERROR_EEPROM_F07               = -70;
  HH_ERROR_EEPROM_F08               = -71;
  HH_ERROR_EEPROM_F09               = -72;
  HH_ERROR_EEPROM_F10               = -73;
  HH_ERROR_EEPROM_F11               = -74;

  //The following are bitmasks for return values from HH_GetWarnings

  WARNING_SYNC_RATE_ZERO            = $0001;
  WARNING_SYNC_RATE_TOO_LOW         = $0002;
  WARNING_SYNC_RATE_TOO_HIGH        = $0004;

  WARNING_INPT_RATE_ZERO            = $0010;
  WARNING_INPT_RATE_TOO_HIGH        = $0040;

  WARNING_INPT_RATE_RATIO           = $0100;
  WARNING_DIVIDER_GREATER_ONE       = $0200;
  WARNING_TIME_SPAN_TOO_SMALL       = $0400;
  WARNING_OFFSET_UNNECESSARY        = $0800;
  {$ENDIF}

  {$IFDEF PH300}
  LIBVERSION = '2.2';

  MAXDEVNUM = 8;
  HISTCHAN = 65536;         // number of histogram channels
  TTREADMAX = 131072;       // 128K event records
  RANGES = 8;

  FLAG_OVERFLOW = $0040;
  FLAG_FIFOFULL = $0003;

  ZCMIN = 0;                //mV
  ZCMAX = 20;               //mV
  DISCRMIN = 0;             //mV
  DISCRMAX = 800;           //mV

  OFFSETMIN = 0;            //ps
  OFFSETMAX = 1000000000;   //ps
  ACQTMIN = 1;              //ms
  ACQTMAX = 36000000;       //ms  (10*60*60*1000ms = 10h)

  ERROR_DEVICE_OPEN_FAIL = -1;
  {$ENDIF}

{##########################################################
###########################################################
##
##  constants used to define events, measurement mode etc.,
##  can be added, e.g. to define a condition that is
##  triggered by different events, or to define a 2-axis or
##  3-axis measurement mode.
##
###########################################################
##########################################################}

  none     =  0;
  PQ_start =  1;
  PQ_stop  =  2;
  PQ_sync  =  4;
  PQ_MA1   =  8;
  PQ_MA2   = 16;
  PQ_MA3   = 32;
  PQ_MA4   = 64;
  auto     =128; // increment/reset condition

  time_axis       = 1;
  sweep_axis      = 2;
  repetition_axis = 4;

  thres_use_none  =  0;
  thres_use_min   =  1;
  thres_use_max   =  2;

  repeat_sweeps     = 0;
  sweep_repetitions = 1;


var
  debug_level    : integer = 0;             // if 1, more information will
                                            // be printed during the measurement
  abort_condition: integer = none;          // event(s) to stop measuring
  {$IFDEF HH400}
  pcLibVers      : pchar;
  strLibVers     : array [0.. 7] of char;
  pcErrText      : pchar;
  strErrText     : array [0..40] of char;
  pcHWSerNr      : pchar;
  strHWSerNr     : array [0.. 7] of char;
  pcHWModel      : pchar;
  strHWModel     : array [0..15] of char;
  pcHWPartNo     : pchar;
  strHWPartNo    : array [0.. 8] of char;
  pcWtext        : pchar;
  strWtext       : array [0.. 16384] of char;

  iDevIdx        : array [0..MAXDEVNUM-1] of longint;
  {$ENDIF}

  {$IFDEF PH300}
  LIB_Version: array[0..7] of char;
  HW_Serial: array[0..7] of char;
  HW_Model: array[0..15] of char;
  HW_Version: array[0..7] of char;
  Errorstring: array[0..40] of char;
  {$ENDIF}


  ret: integer;             // picoharp/ hydraharp library call return value
                            // picoharp: number of events in TTTR FIFO buffer
  size: integer;            // hydraharp: number of events in TTTR FIFO buffer
  dev: integer = 0;         // device number for pico/hydraharp library calls
  measuring: boolean;       // True indicates tha data processing is active;
                            // if False, measurement will be aborted.
  start_cnt: integer = 0;   // global counter of start events
  stop_cnt: integer = 0;    // global counter of stop events
  sync_cnt: integer = 0;    // global counter of sync events
  ovl_cnt: integer = 0;     // global counter of timer overflow events
  ma1_cnt: integer;         // global counter of marker 1 events
  ma2_cnt: integer;         // global counter of marker 2 events
  ma3_cnt: integer;         // global counter of marker 3 events
  ma4_cnt: integer;         // global counter of marker 4 events
  overflow: longint;        // if timer overflow occurs, max. timer value is
                            // added to overflow (is re-set with detection of
                            // a section increment event.
  time0: longint;           // timer value at detection of section increment
                            // event.
  time1: longint;           // timer value at detection of section event.
  dt: longint;              // time1 - time0 + overflow, time difference between
                            // section increment and section event (in units of
                            // device base resolution)
  data_index: integer;      // address of current event within section's data
                            // array
  event: integer;           // current event (e.g. PQ_start, PQ_MA1 etc.)
  incr_section: Integer;    // normally set to 0. set to auto, if a section
                            // event occurs after duration of the actual section
                            // (enables automatic incrementation of section)
  just_started: Integer;    // special condition, set to 1 when data processing
                            // is started, and reset to 0 after receiving first
                            // section increment
  sections_active: integer; // set to 1 if events can be assigned to a section
  section_index: longint;   // index of the currently active section
  section_count: integer;   // number of measurement sections
  reset_section: Integer;   // go to first section
  initialize_section: Integer; // in conditional mode: if set to 1: prepare
                            // temporary dataarray to store events before a
                            // decision is taken if this sequence fullfills all
                            // thresholds or not.
  sweeps_active: integer;   // set to 1 if events can be assigned to a sweep
                            // value
  repetitions_active: integer; // set to 1 if events can be assigned to a
                            // repetition value
  reset_sweep: Integer;     // normally 0. set to auto to enable automatic
                            // sweep index reset
  reset_repetition: Integer;// normally 0. set to auto to enable automatic
                            // repetition index reset
  incr_sweep: Integer;      // normally 0. set to auto to enable automatic
                            // sweep increment
  incr_repetition: Integer; // normally 0. set to auto to enable automatic
                            // repetition increment
  sweep_index: longint;     // current index within sweep
  repetition_index: longint;// current index within repetitions
  bin_index: longint;       // index of time-bin for current event within
                            // current section

  flags, FiFoWasFull, CTCDone: integer; // return values of pico(hydra)harp
                                        // library calls
  Progress: integer;        // current measurement progress in %
  blocksz: integer = TTREADMAX;  // maximum block size to read from
                            // TTTR mode FIFO buffer
  buffer: array[0..TTREADMAX - 1] of cardinal; // FIFO buffer to read event
                            // record from pico(hydra)harp
  time: integer;            // time stamp of detected event

  {$IFDEF HH400}
  meastime_d: double;       // total measurement time (hydraharp: float)
  {$ENDIF HH400}
  meastime: integer;        // total measurement time (picoharp: integer)

  sections: array of section_type; // array to store list of sequence sections
                            // (length is adjusted when adding a section)

{$IFDEF HH400}
{the following are the functions exported by HHLIB.DLL}
function  HH_GetLibraryVersion     (vers : pchar) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetErrorString        (errstring : pchar; errcode : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_OpenDevice            (devidx : longint; serial : pchar) : longint;
  stdcall; external 'hhlib.dll';
function  HH_CloseDevice           (devidx : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_Initialize            (devidx : longint; mode : longint; refsource : longint) : longint;
  stdcall; external 'hhlib.dll';

// all functions below can only be used after HH_Initialize

function  HH_GetHardwareInfo       (devidx : longint; model : pchar; partno : pchar) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetSerialNumber       (devidx : longint; serial : pchar) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetBaseResolution     (devidx : longint; var resolution : double; var binsteps : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_GetNumOfInputChannels (devidx : longint; var nchannels : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetNumOfModules       (devidx : longint; var nummod : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetModuleInfo         (devidx : longint; modidx : longint; var modelcode : longint; var versioncode : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetModuleIndex        (devidx : longint; channel : longint; var modidx : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_Calibrate             (devidx : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_SetSyncDiv            (devidx : longint; syncdiv : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetSyncCFDLevel       (devidx : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetSyncCFDZeroCross   (devidx : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetSyncChannelOffset  (devidx : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_SetInputCFDLevel      (devidx : longint; channel : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetInputCFDZeroCross  (devidx : longint; channel : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetInputChannelOffset (devidx : longint; channel : longint; value : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_SetStopOverflow       (devidx : longint; stop_ovfl : longint; stopcount : longword) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetBinning            (devidx : longint; binning : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetOffset             (devidx : longint; offset : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetHistoLen           (devidx : longint; lencode : longint; var actuallen : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_ClearHistMem          (devidx : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_StartMeas             (devidx : longint; tacq : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_StopMeas              (devidx : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_CTCStatus             (devidx : longint; var ctcstatus : longint) : longint;
  stdcall; external 'hhlib.dll';

function  HH_GetHistogram          (devidx : longint; var chcount : longword; channel : longint; clear : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetResolution         (devidx : longint; var resolution : double) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetSyncRate           (devidx : longint; var syncrate : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetCountRate          (devidx : longint; channel : longint; var cntrate : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetFlags              (devidx : longint; var flags : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetElapsedMeasTime    (devidx : longint; var elapsed : double) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetWarnings           (devidx : longint; var warnings : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_GetWarningsText       (devidx : longint; model : pchar; warnings : longint) : longint;
  stdcall; external 'hhlib.dll';

// for TT modes

function  HH_SetMarkerEdges      (devidx : longint; me1 : longint; me2 : longint; me3 : longint; me4 : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_SetMarkerEnable     (devidx : longint; en1 : longint; en2 : longint; en3 : longint; en4 : longint) : longint;
  stdcall; external 'hhlib.dll';
function  HH_ReadFiFo            (devidx : longint; buffer : Plong; count : longint; var nactual : longint) : longint;
  stdcall; external 'hhlib.dll';
{$ENDIF}

{$IFDEF PH300}
{the following are the functions exported by PHLIB.DLL}
function PH_GetLibraryVersion(LIB_Version: PChar): integer;
  stdcall; external 'phlib.dll';
function PH_GetErrorString(errstring: PChar; errcode: integer): integer;
  stdcall; external 'phlib.dll';
function PH_OpenDevice(devidx: integer; serial: PChar): integer; //new in v2.0
  stdcall; external 'phlib.dll';
function PH_CloseDevice(devidx: integer): integer;  //new in v2.0
  stdcall; external 'phlib.dll';
function PH_Initialize(devidx: integer; mode: integer): integer;
  stdcall; external 'phlib.dll';
function PH_GetHardwareVersion(devidx: integer; model: PChar; vers: PChar): integer;
  stdcall; external 'phlib.dll';
function PH_GetSerialNumber(devidx: integer; serial: PChar): integer;
  stdcall; external 'phlib.dll';
function PH_GetBaseResolution(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_Calibrate(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetSyncDiv(devidx: integer; divd: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetCFDLevel(devidx: integer; channel, Value: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetCFDZeroCross(devidx: integer; channel, Value: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetStopOverflow(devidx: integer; stop_ovfl, stopcount: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetRange(devidx: integer; range: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetOffset(devidx: integer; offset: integer): integer;
  stdcall; external 'phlib.dll';
function PH_ClearHistMem(devidx: integer; block: integer): integer;
  stdcall; external 'phlib.dll';
function PH_StartMeas(devidx: integer; tacq: integer): integer;
  stdcall; external 'phlib.dll';
function PH_StopMeas(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_CTCStatus(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_GetBlock(devidx: integer; chcount: Plong; block: longint): integer;
  stdcall; external 'phlib.dll';
function PH_GetResolution(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_GetCountRate(devidx: integer; channel: integer): integer;
  stdcall; external 'phlib.dll';
function PH_GetFlags(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_GetElapsedMeasTime(devidx: integer): integer;
  stdcall; external 'phlib.dll';

//for routing:
function PH_GetRouterVersion(devidx: integer; model: PChar; version: PChar): integer;
  //new in v2.0
  stdcall; external 'phlib.dll';
function PH_GetRoutingChannels(devidx: integer): integer;
  stdcall; external 'phlib.dll';
function PH_EnableRouting(devidx: integer; enable: integer): integer;
  stdcall; external 'phlib.dll';
function PH_SetPHR800Input(devidx: integer; channel: integer;
  level: integer; edge: integer): integer;  //new in v2.0
  stdcall; external 'phlib.dll';
function PH_SetPHR800CFD(devidx: integer; channel: integer; dscrlevel: integer;
  zerocross: integer): integer; //new in v2.0
  stdcall; external 'phlib.dll';

//for TT modes
function PH_TTReadData(devidx: integer; buffer: Plong; Count: cardinal): integer;
  stdcall; external 'phlib.dll';
{$ENDIF}

procedure set_dev(dev_idx:integer); stdcall;
begin
  dev := dev_idx;
end;

function start(Tacq: integer): integer; stdcall; // Tacq: measurement time in ms
begin
  writeln('');
  writeln('');
  writeln('universal measurementDLL v1.0');
  writeln('~~~~~~~~~~~~~~~~~~~');
  {$IFDEF HH400}
  writeln(' version for HydraHarp 400');
  HH_GetLibraryVersion (pcLibVers);
  pcLibVers  := PChar(@strLibVers[0]);
  writeln('HHLIB.DLL version is ' + strLibVers);
  ret := HH_StartMeas(dev, Tacq);
  {$ENDIF}
  {$IFDEF PH300}
  writeln(' version for PicoHarp 300');
  PH_GetLibraryVersion(LIB_Version);
  writeln('PHLIB.DLL version is ' + LIB_Version);
  ret := PH_StartMeas(dev, Tacq);
  {$ENDIF}
  if ret < 0 then
  begin
    writeln;
    writeln('Error in StartMeas. Aborted.');
    measuring := False;
    Result := -1;
  end
  else
  begin
    {$IFDEF HH400}
    writeln('HydraHarp 400: data acquisition started.');
    {$ENDIF}
    {$IFDEF PH300}
    writeln('PicoHarp 300: data acquisition started.');
    {$ENDIF}
    Result := 0;
  end;
end;

procedure set_debuglevel(level: integer); stdcall; // level = 1 for debug info
begin
  debug_level := level;
end;

procedure set_abort_condition(event: integer); stdcall; // event(s) to stop
                                                        // measurement
begin
  abort_condition := event;
end;

procedure write_events(event: integer); // for debug: print event(s) name(s)
begin
  if event = none then
    writeln('##    - none');
  if (event and PQ_start) > 0 then
    writeln('##    - start');
  if (event and PQ_stop) > 0 then
    writeln('##    - stop');
  if (event and PQ_sync) > 0 then
    writeln('##    - sync');
  if (event and PQ_MA1) > 0 then
    writeln('##    - marker 1');
  if (event and PQ_MA2) > 0 then
    writeln('##    - marker 2');
  if (event and PQ_MA3) > 0 then
    writeln('##    - marker 3');
  if (event and PQ_MA4) > 0 then
    writeln('##    - marker 4');
  if (event and auto) > 0 then
    writeln('##    - automatic');
end;

function add_section( // add a measurement section. data needs to be the pointer
                      // to a properly dimensioned numpy array of type uint32,
                      // initialized to zero.
  event_type: integer;
  bin_size: Integer;
  offset: Integer;
  duration: Integer;
  mode: Integer;
  threshold_min: Integer;
  threshold_max: Integer;
  threshold_mode:Integer;
  reset_mode:Integer;
  data:Plong): integer; stdcall;
var
  l: integer;
begin
  l := Length(sections);
  SetLength(sections, l + 1);
  sections[l].event_type      := event_type and (PQ_start + PQ_stop +
                              PQ_sync + PQ_MA1 + PQ_MA2 + PQ_MA3 + PQ_MA4);
  sections[l].bin_size        := bin_size;
  sections[l].offset          := offset;
  sections[l].duration        := duration;
  sections[l].mode            := mode;
  sections[l].threshold_min   := threshold_min;
  sections[l].threshold_max   := threshold_max;
  sections[l].threshold_mode  := threshold_mode;
  sections[l].reset_mode      := reset_mode;
  sections[l].data            := data;
  begin
    if debug_level > 0 then
    begin
      writeln('');
      writeln('############################################################');
      writeln('##');
      writeln('##   universal TTTR measurement: section ', l+1, ' added:');
      writeln('##   events to be counted:');
      write_events(sections[l].event_type);
      writeln('##');
      writeln('##   binsize: ', bin_size);
      writeln('##   offset: ', offset);
      writeln('##   duration: ', duration);
      writeln('##');
      writeln('##   dimensionality of data:');
      if (sections[l].mode and time_axis) > 0 then
        writeln('##    - time axis');
      if (sections[l].mode and sweep_axis) > 0 then
        writeln('##    - sweep axis');
      if (sections[l].mode and repetition_axis) > 0 then
        writeln('##    - repetition axis');
      writeln('##');
      if (sections[l].threshold_mode = 0) then
        writeln('##   no threshold condition');
      if (sections[l].threshold_mode and thres_use_min) > 0 then
        writeln('##   threshold condition: more than ',sections[l].threshold_min,' counts.');
      if (sections[l].threshold_mode and thres_use_max) > 0 then
        writeln('##   threshold condition: less than ',sections[l].threshold_max,' counts.');
      writeln('##');
      writeln('##   events to reset section:');
      write_events(sections[l].reset_mode);
      writeln('##');
      writeln('##');
    end;
  end;
  SetLength(sections[l].temp_data, 0);
  Result := l + 1;
end;

function clear_sections(): integer; stdcall; // remove previously defined
                                             // measurement sections
var l,m : integer;
begin
  l := Length(sections);
  for m:=0 to l-1 do
    SetLength(sections[m].temp_data, 0);
  SetLength(sections,0);
  Result := Length(sections);
end;

function determine_event_type(buffer: cardinal): integer; // determine event
                                             // type from pico(hydra)harp
                                             // raw TTTR-mode2 data
var
  event: integer;
  channel: integer;
  special: integer;

begin
  {$IFDEF HH400}
  special := buffer shr 31;
             // 1: channel = 0 -> sync, channel = 63 -> overflow
             //    channel = 1,2,4,8 -> MA1 .. MA4
             // 0: channel = 0 -> start, channel = 1 -> stop

  channel := (buffer shr 25) and 63;

  //and 33554431;       // = 2**25-1
             // 0: overflow, 1..3: MA1..MA3

  ////////////////////////////////////////////////////////////////////////
  // determine event type
  case special of
    1:  case channel of
          63: begin
                event := none;
                overflow += 33554432;   // ???
                ovl_cnt += 1;
              end;
          0:  begin
                event := PQ_sync;
                sync_cnt += 1;
              end
          otherwise
            case (channel and 15) of
              1: begin
                   event := PQ_MA1;
                   ma1_cnt += 1;
                 end;
              2: begin
                   event := PQ_MA2;
                   ma2_cnt += 1;
                 end;
              4: begin
                   event := PQ_MA3;
                   ma3_cnt += 1;
                 end;
              8: begin
                   event := PQ_MA4;
                   ma4_cnt += 1;
                 end;
            end;
        end;
    0:  case channel of
          0: begin
               event := PQ_start;
               start_cnt += 1;
             end;
          1: begin
               event := PQ_stop;
               stop_cnt += 1;
             end;
        end;
  end;
  {$ENDIF}
  {$IFDEF PH300}
  channel := (buffer shr 28) and 15;
             // 0: start, 1: stop, else 'special'.
  special := buffer and 15;
             // 0: overflow, 1..3: MA1..MA3

  ////////////////////////////////////////////////////////////////////////
  // determine event type
  case channel of
    0:  begin
          event := PQ_start;
          start_cnt += 1;
        end;
    1:  begin
          event := PQ_stop;
          stop_cnt += 1;
        end
    otherwise
      case special of
        0:  begin
              event := none;
              overflow += 210698240;
              ovl_cnt += 1;
            end;
        1:  begin
              event := PQ_MA1;
              ma1_cnt += 1;
            end;
        2:  begin
              event := PQ_MA2;
              ma2_cnt += 1;
            end;
        3:  begin
              event := PQ_MA3;
              ma3_cnt += 1;
            end;
        otherwise event := none
      end
  end;
  {$ENDIF}
  Result:= event;
end;

procedure do_initialize_section(); // prepare temporary data array for
                                   // conditional mode
var j:integer;
begin
  if (sections[section_index].mode and time_axis) > 0 then
  begin
    SetLength(sections[section_index].temp_data,sections[section_index].duration);
    for j:= 0 to sections[section_index].duration-1 do
      sections[section_index].temp_data[j]:=0
  end else begin
    SetLength(sections[section_index].temp_data, 1);
    sections[section_index].temp_data[0]:=0
  end;
  sections[section_index].counts:=0;
end;

procedure do_increment_section(); // handle loop behaviour for section
                                  // increment event
begin
  // increment section
  incr_section := 0;
  time0 := time;
  overflow := 0;
  if just_started = 1 then
  begin
    just_started   := 0;
    sections_active := 1;
    section_index  := 0;
  end else if sections_active = 1 then section_index += 1;
  if section_index >= section_count then
  begin
    section_index    := 0;
    reset_section    := auto;
    sections_active  := 0;
  end;
  initialize_section := 1;
end;

procedure do_reset_section(loop_order: integer); // handle loop behaviour for
                                                 // section reset event
begin
  // restart sections
  reset_section := 0;
  section_index := 0;
  sections_active:=1;
  time0 := time;
  overflow := 0;
  if (repetitions_active=1) and (sweeps_active=1)
         and (measuring = True) then
    if loop_order = repeat_sweeps then
    begin
      incr_sweep := auto;
    end else begin
      incr_repetition := auto;
    end;
end;

procedure do_loop_increment(loop_order, sweep_inc_cond, sweep_res_cond,
            rep_inc_cond, rep_res_cond, sweeps, repetitions: integer);
            // handle loop behaviour for sweeps and repetitions
begin
  ////////////////////////////////////////////////////////////////////////
  // loop behaviour
  if loop_order = repeat_sweeps then
  begin
    if ((event or incr_sweep) and sweep_inc_cond) > 0 then
    begin
      incr_sweep:=0;
      // increment sweep (inner loop)
      sweep_index += 1;
      if sweep_index >= sweeps then begin
        sweep_index := 0;
        reset_sweep := auto;
        sweeps_active := 0;
      end;
    end;
    if ((event or reset_sweep) and sweep_res_cond) > 0 then
    begin
      // start new sweep (inner loop)
      reset_sweep := 0;
      sweep_index := 0;
      sweeps_active := 1;
      incr_repetition := auto;
      //just_started := 1;
    end;
    if ((event or incr_repetition) and rep_inc_cond) > 0 then
    begin
      // increment repetition (outer loop)
      incr_repetition := 0;
      repetition_index += 1;
      if repetition_index >= repetitions then begin
        reset_repetition := auto;
        repetitions_active := 0;
        measuring := False;
      end;
    end;
    if ((event or reset_repetition) and rep_res_cond) > 0 then
    begin
      // start new repetition (outer loop) => measurement finished
      reset_repetition := 0;
      measuring := False;
    end
  end else begin
    if ((event or incr_repetition) and rep_inc_cond) > 0 then
    begin
      // increment repetition (inner loop)
      incr_repetition := 0;
      repetition_index += 1;
      if repetition_index >= repetitions then begin
        reset_repetition := auto;
        repetitions_active := 0;
      end;
    end;
    if ((event or reset_repetition) and rep_res_cond) > 0 then
    begin
      // start new repetition (inner loop)
      reset_repetition := 0;
      repetition_index := 0;
      repetitions_active := 1;
      incr_sweep := auto;
      //just_started := 1;
    end;
    if ((event or incr_sweep) and sweep_inc_cond) > 0 then
    begin
      // increment sweep (outer loop)
      incr_sweep := 0;
      sweep_index += 1;
      if sweep_index >= sweeps then begin
        reset_sweep := auto;
        sweeps_active := 0;
        measuring := False;
      end;
    end;
    if ((event or reset_sweep) and sweep_res_cond) > 0 then
    begin
      // start new sweep (outer loop)
      reset_sweep := 0;
      measuring := False;
    end;
  end;
end;

function TTTR2_universal_measurement(
  sweeps: integer;             // number of sweep steps
  repetitions: integer;        // number of repetitions
  sweep_inc_cond: integer;     // condition for sweep increment
  sweep_res_cond: integer;     // condition for sweep reset
  rep_inc_cond: integer;       // condition for repetition increment
  rep_res_cond: integer;       // condition for repetition reset
  sec_inc_cond: integer;       // condition for section increment
  seq_res_cond: integer;       // condition for sequence reset
  loop_order: integer;         // 0: repeat sweeps
                               // 1: sweep repetitions
  statistics: Plong            // Array with counter variables:
                               //  - 'start' events
                               //  - 'stop' events
                               //  - 'sync' events
                               //  - 'MA1' events
                               //  - 'MA2' events
                               //  - 'MA3' events
                               //  - 'MA4' events
                               //  - 'OFL' events
                               //  - sweep index
                               //  - repetition index
                               //  - valid section n (1d array, length n)
  ): integer; stdcall;

var
  last_progress: integer = 0;  // temporary variable to determine measurement
                               // progress
  progress: longint;           // current measurement progress in %
  i,j,k: integer;              // loop indices
  x,y,z: integer;              // loop indices
  u,v,w: integer;              // loop indices
  valid: Integer;              // set to 0 if a threshold condition fails
  valid_counter: longint;      // counter of valid sequence runs
  invalid_counter: longint;    // counter of invalid sequence runs
  detected_events: longint;    // total detected events in valid sequence runs

begin
  section_count := Length(sections);

  writeln('');
  writeln('generalized T2 mode measurement (conditional mode):');
  writeln(' - repetitions: ', repetitions);
  writeln(' - sweeps:      ', sweeps);
  writeln(' - sections:    ', section_count);
  writeln('');
  writeln('');
  if debug_level > 0 then
  begin
    writeln('##   events to increment section:');
    write_events(sec_inc_cond);
    writeln('##');

    writeln('##   events to reset sequence:');
    write_events(seq_res_cond);
    writeln('##');

    writeln('##   events to increment sweep:');
    write_events(sweep_inc_cond);
    writeln('##');

    writeln('##   events to reset sweep:');
    write_events(sweep_res_cond);
    writeln('##');

    writeln('##   events to reset repetitions:');
    write_events(rep_res_cond);
    writeln('##');

    writeln('##   events to increment repetitions:');
    write_events(rep_inc_cond);
    writeln('##');

    writeln('##   events to abort measurement:');
    write_events(abort_condition);
    writeln('##');

    if loop_order = repeat_sweeps then
      writeln('##   sweep order: repeat sweeps')
    else
      writeln('##   sweep order: sweep repetitions');
    writeln('##');
  end;

  stop_cnt := 0;
  sync_cnt := 0;
  start_cnt := 0;
  ovl_cnt := 0;
  ma1_cnt := 0;
  ma2_cnt := 0;
  ma3_cnt := 0;
  ma4_cnt := 0;
  measuring := True;
  Result := 0;
  sections_active:=0;
  sweeps_active:=1;
  repetitions_active:=1;
  incr_sweep :=0;
  incr_repetition :=0;
  incr_section :=0;
  reset_section :=0;
  reset_sweep :=0;
  reset_repetition :=0;
  section_index:= 0;
  bin_index:= 0;
  sweep_index:= 0;
  repetition_index:= 0;
  just_started := 1;
  valid_counter := 0;
  invalid_counter := 0;
  detected_events := 0;

  do_initialize_section();

  while measuring do
  begin
    {$IFDEF HH400}
    ret := HH_GetFlags(dev, flags);
    {$ENDIF}
    {$IFDEF PH300}
    flags := PH_GetFlags(dev);
    {$ENDIF}
    FiFoWasFull := flags and FLAG_FIFOFULL;
    if FiFoWasFull <> 0 then
    begin
      writeln;
      writeln('FiFo Overrun!');
      measuring := False;
      Result := -1;
    end;
    {$IFDEF HH400}
    ret := HH_ReadFiFo(dev, @buffer[0], blocksz, size);
    {$ENDIF}
    {$IFDEF PH300}
    ret := PH_TTReadData(dev, @buffer[0], blocksz);
    {$ENDIF}
    if loop_order = 0 then
      progress := round(repetition_index * 100 div repetitions)
    else
      progress := round(sweep_index * 100 div sweeps);
    if progress <> last_progress then
    begin
      last_progress := progress;
      writeln(progress, '%');
    end;
    if ret < 0 then
    begin
      writeln;
      writeln('ReadData error ', ret);
      measuring := False;
      Result := -1;
    end
    {$IFDEF HH400}
    else if size > 0 then
    begin
      for i := 0 to size - 1 do
      {$ENDIF}
    {$IFDEF PH300}
    else if ret > 0 then
    begin
      for i := 0 to ret - 1 do
      {$ENDIF}
        if measuring = True then
        begin
          {$IFDEF HH400}
          time := buffer[i] and 33554431;
          // time since last timer overflow event in units of 1ps.
          {$ENDIF}
          {$IFDEF PH300}
          time := buffer[i] and 268435455;
          // time since last timer overflow event in units of 4ps.
          {$ENDIF}

          event := determine_event_type(buffer[i]);

          if (event and abort_condition) > 0 then
          begin
            writeln('Measurement aborted: detected');
            write_events(event);
            measuring := False;
          end;

          if (event and sections[section_index].reset_mode) > 0 then
            do_initialize_section();

          ////////////////////////////////////////////////////////////////////////
          // count event (event to be counted in this section)
          if ((event and sections[section_index].event_type) > 0) and
             (sections_active=1) and (repetitions_active=1) and
             (sweeps_active=1) and (measuring = True) then
          begin
            time1 := time + overflow;
            dt := time1 - time0;
            bin_index := dt div (1 shl sections[section_index].bin_size) -
              sections[section_index].offset;
            if (bin_index >= 0) and
              (bin_index < sections[section_index].duration) then
            begin
              // evaluate count event
              if (sections[section_index].mode and time_axis) > 0 then
                sections[section_index].temp_data[bin_index]+=1;
              sections[section_index].counts+=1;
            end;
            if bin_index >= sections[section_index].duration then
              incr_section := auto;
          end;

          ////////////////////////////////////////////////////////////////////////
          // section change
          initialize_section:=0;

          if ((event or incr_section) and sec_inc_cond) > 0 then
            do_increment_section();

          if ((event or reset_section) and seq_res_cond) > 0 then
          begin
            // restart sections
            reset_section := 0;
            section_index := 0;
            sections_active:=1;
            time0 := time;
            overflow := 0;
            initialize_section := 1;

            if (repetitions_active=1) and (sweeps_active=1) and
                   (measuring = True) then
            begin
              // check if measurement is valid (-> threshold conditions)
              valid := 1;  // sequence is valid by default
              for j := 0 to section_count - 1 do
              begin
                if (((sections[j].threshold_mode and thres_use_min) > 0) and
                       (sections[j].counts < sections[j].threshold_min)) or
                   (((sections[j].threshold_mode and thres_use_max) > 0) and
                       (sections[j].counts > sections[j].threshold_max)) then
                       valid := 0 // threshold not met -> sequence invalidated
                         else
                           statistics[14+j] += 1; // valid section
              end;

              if valid = 1 then
              begin
                valid_counter += 1;
              // store data
                for j := 0 to section_count - 1 do
                begin
                  if (sections[j].mode and time_axis) > 0 then begin
                    x := sections[j].duration;
                    u := 1;
                  end else begin
                    x := 1;
                    u := 0;
                  end;
                  if (sections[j].mode and sweep_axis) > 0 then begin
                    y := sweeps;
                    v := 1;
                  end else begin
                    y := 1;
                    v := 0;
                  end;
                  if (sections[j].mode and repetition_axis) > 0 then begin
                    z := repetitions;
                    w := 1;
                  end else begin
                    z := 1;
                    w := 0;
                  end;

                  if (sections[j].mode and time_axis) > 0 then
                    for k := 0 to x - 1 do
                    begin
                      detected_events += sections[j].temp_data[k];
                      data_index := u*k + v*x*sweep_index + w*x*y*repetition_index;
                      sections[j].data[data_index]+=sections[j].temp_data[k];
                    end
                  else
                    begin
                      detected_events += sections[j].counts;
                      data_index := v*x*sweep_index + w*x*y*repetition_index;
                      sections[j].data[data_index]+=sections[j].counts;
                    end;
                end;
              end else invalid_counter += 1;

              if loop_order = repeat_sweeps then
                begin
                  if valid = 1 then incr_sweep := auto;
                end
              else
                begin
                  if valid = 1 then incr_repetition := auto;
                end;
            end;
          end;

          if initialize_section = 1 then
            do_initialize_section();

          do_loop_increment(loop_order, sweep_inc_cond, sweep_res_cond,
            rep_inc_cond,rep_res_cond, sweeps, repetitions);
        end;
    end
    else
      begin
        {$IFDEF HH400}
        ret := HH_CTCStatus(dev, CTCDone);
        {$ENDIF}
        {$IFDEF PH300}
        CTCDone := PH_CTCStatus(dev);
        {$ENDIF}
        if CTCDone <> 0 then
        begin
          writeln('measurement time elapsed');
          measuring := False;
        end;
      end;
  end;

  {$IFDEF HH400}
  HH_StopMeas(dev);
  ret := HH_GetElapsedMeasTime(dev, meastime_d);
  meastime := round(meastime_d);
  {$ENDIF}
  {$IFDEF PH300}
  PH_StopMeas(dev);
  meastime := PH_GetElapsedMeasTime(dev);
  {$ENDIF}

  writeln;
  if loop_order = repeat_sweeps then
    writeln('repetitions completed: ', repetition_index, '/', repetitions, ' (',sweeps,' sweep(s))')
  else
    writeln('sweeps completed: ', sweep_index, '/', sweeps, '(',repetitions,' repetition(s))');
  writeln;
  writeln('conditioning: ', valid_counter, ' valid sequences and ',invalid_counter,' invalid sequences');
//  if (valid_counter + invalid_counter) > 0 then
//    writeln('              ', ((valid_counter * 10000) div (valid_counter + invalid_counter))/100,'% valid events');
  writeln;
  writeln('marker 1: ', ma1_cnt, ', marker 2: ', ma2_cnt,', marker 3: ',ma3_cnt,', marker 4: ',ma4_cnt);
  writeln('starts: ', start_cnt, ', stops: ', stop_cnt, ', syncs: ', sync_cnt, ', overflow events: ', ovl_cnt);
  writeln('detected events: ', detected_events);
  writeln;
  writeln('Measurement time: ',meastime, 'ms');
  if (meastime / 1000) > 0 then
    writeln('Average data rate: ', round((ma1_cnt + ma2_cnt + ma3_cnt + ma4_cnt + start_cnt + stop_cnt + sync_cnt + ovl_cnt) * 1000 / (meastime)), ' events/s');
  statistics[0] := start_cnt;
  statistics[1] := stop_cnt;
  statistics[2] := sync_cnt;
  statistics[3] := ma1_cnt;
  statistics[4] := ma2_cnt;
  statistics[5] := ma3_cnt;
  statistics[6] := ma4_cnt;
  statistics[7] := ovl_cnt;
  statistics[8] := meastime;
  statistics[9] := sweep_index;
  statistics[10] := repetition_index;
  statistics[11] := detected_events;
  statistics[12] := valid_counter;
  statistics[13] := invalid_counter;
end;

function TTTR2_universal_measurement_speedmode_unconditional(
  sweeps: longint;             // number of sweep steps
  repetitions: longint;        // number of repetitions
  sweep_inc_cond: integer;     // condition for sweep increment
  sweep_res_cond: integer;     // condition for sweep reset
  rep_inc_cond: integer;       // condition for repetition increment
  rep_res_cond: integer;       // condition for repetition reset
  sec_inc_cond: integer;       // condition for section increment
  seq_res_cond: integer;       // condition for sequence reset
  loop_order: integer;         // 0: repeat sweeps
                               // 1: sweep repetitions
  statistics: Plong            // Array with counter variables:
                               //  - 'start' events
                               //  - 'stop' events
                               //  - 'sync' events
                               //  - 'MA1' events
                               //  - 'MA2' events
                               //  - 'MA3' events
                               //  - 'MA4' events
                               //  - 'OFL' events
                               //  - sweep index
                               //  - repetition index
                               //  - valid section n (1d array, length n)
  ): integer; stdcall;

var
  last_progress: integer = 0;  // temp. var. to determine measurement progress
  progress: longint;           // current measurement progress in %
  i: integer;                  // loop variable
  detected_events: longint;    // total detected events

begin
  section_count := Length(sections);
  writeln('');
  writeln('generalized T2 mode measurement (unconditional mode):');
  writeln(' - repetitions: ', repetitions);
  writeln(' - sweeps:      ', sweeps);
  writeln(' - sections:    ', section_count);
  writeln('');
  writeln('');
  if debug_level > 0 then
  begin
    writeln('##   events to increment section:');
    write_events(sec_inc_cond);
    writeln('##');

    writeln('##   events to reset sequence:');
    write_events(seq_res_cond);
    writeln('##');

    writeln('##   events to increment sweep:');
    write_events(sweep_inc_cond);
    writeln('##');

    writeln('##   events to reset sweep:');
    write_events(sweep_res_cond);
    writeln('##');

    writeln('##   events to reset repetitions:');
    write_events(rep_res_cond);
    writeln('##');

    writeln('##   events to increment repetitions:');
    write_events(rep_inc_cond);
    writeln('##');

    writeln('##   events to abort measurement:');
    write_events(abort_condition);
    writeln('##');

    if loop_order = repeat_sweeps then
      writeln('##   sweep order: repeat sweeps')
    else
      writeln('##   sweep order: sweep repetitions');
    writeln('##');
  end;

  stop_cnt := 0;
  sync_cnt := 0;
  start_cnt := 0;
  ovl_cnt := 0;
  ma1_cnt := 0;
  ma2_cnt := 0;
  ma3_cnt := 0;
  ma4_cnt := 0;
  measuring := True;
  Result := 0;
  sections_active:=0;
  sweeps_active:=1;
  repetitions_active:=1;
  incr_sweep :=0;
  incr_repetition :=0;
  incr_section :=0;
  reset_sweep :=0;
  reset_repetition :=0;
  reset_section :=0;
  section_index :=0;
  bin_index := 0;
  repetition_index := 0;
  sweep_index := 0;
  bin_index:= 0;
  just_started := 1;
  detected_events := 0;

  while measuring do
  begin
    {$IFDEF HH400}
    ret := HH_GetFlags(dev, flags);
    {$ENDIF}
    {$IFDEF PH300}
    flags := PH_GetFlags(dev);
    {$ENDIF}
    FiFoWasFull := flags and FLAG_FIFOFULL;
    if FiFoWasFull <> 0 then
    begin
      writeln;
      writeln('FiFo Overrun!');
      measuring := False;
      Result := -1;
    end;
    {$IFDEF HH400}
    ret := HH_ReadFiFo(dev, @buffer[0], blocksz, size);
    {$ENDIF}
    {$IFDEF PH300}
    ret := PH_TTReadData(dev, @buffer[0], blocksz);
    {$ENDIF}
    if loop_order = 0 then
      progress := round(repetition_index * 100 div repetitions)
    else
      progress := round(sweep_index * 100 div sweeps);
    if progress <> last_progress then
    begin
      last_progress := progress;
      writeln(progress, '%');
    end;
    if ret < 0 then
    begin
      writeln;
      writeln('ReadData error ', ret);
      measuring := False;
      Result := -1;
    end
    {$IFDEF HH400}
    else if size > 0 then
    begin
      for i := 0 to size - 1 do
      {$ENDIF}
    {$IFDEF PH300}
    else if ret > 0 then
    begin
      for i := 0 to ret - 1 do
      {$ENDIF}
        if measuring = True then
        begin
          {$IFDEF HH400}
          time := buffer[i] and 33554431;
          // time since last timer overflow event in units of 1ps.
          {$ENDIF}
          {$IFDEF PH300}
          time := buffer[i] and 268435455;
          // time since last timer overflow event in units of 4ps.
          {$ENDIF}

          event := determine_event_type(buffer[i]);

          if (event and abort_condition) > 0 then
          begin
            writeln('Measurement aborted: detected');
            write_events(event);
            measuring := False;
          end;

          //////////////////////////////////////////////////////////////////////
          // count event (event to be counted in this section)
          if ((event and sections[section_index].event_type) > 0) and
             (sections_active=1) and (repetitions_active=1) and
             (sweeps_active=1) and (measuring = True) then
          begin
            time1 := time + overflow;
            dt := time1 - time0;
            bin_index := dt div (1 shl sections[section_index].bin_size) -
              sections[section_index].offset;
            if (bin_index >= 0) and
              (bin_index < sections[section_index].duration) then
            // evaluate count event
            begin
              detected_events += 1;
              case sections[section_index].mode of
                 time_axis:
                       begin
                         sections[section_index].data[bin_index] += 1;
                       end;
                 sweep_axis:
                       begin
                         sections[section_index].data[sweep_index] += 1;
                       end;
                 repetition_axis:
                       begin
                         sections[section_index].data[repetition_index] += 1;
                       end;
                 time_axis + sweep_axis:
                       begin
                         sections[section_index].data[bin_index + sections[section_index].duration*sweep_index] += 1;
                       end;
                 sweep_axis + repetition_axis:
                       begin
                         sections[section_index].data[sweep_index+sweeps*repetition_index] += 1;
                       end;
                 time_axis + repetition_axis:
                       begin
                         sections[section_index].data[bin_index+sections[section_index].duration*repetition_index] += 1;
                       end;
                 time_axis + repetition_axis + sweep_axis:
                       begin
                         sections[section_index].data[bin_index+sections[section_index].duration*sweep_index +
                                sections[section_index].duration*sweeps*repetition_index] += 1;
                       end
              end;
            end;

            if bin_index >= sections[section_index].duration then
              incr_section := auto;
          end;

          ////////////////////////////////////////////////////////////////////////
          // section change

          if ((event or incr_section) and sec_inc_cond) > 0 then
            do_increment_section();

          if ((event or reset_section) and seq_res_cond) > 0 then
            do_reset_section(loop_order);

          do_loop_increment(loop_order, sweep_inc_cond, sweep_res_cond,
            rep_inc_cond,rep_res_cond, sweeps, repetitions);
        end;
    end
    else
      begin
        {$IFDEF HH400}
        ret := HH_CTCStatus(dev, CTCDone);
        {$ENDIF}
        {$IFDEF PH300}
        CTCDone := PH_CTCStatus(dev);
        {$ENDIF}
        if CTCDone <> 0 then
        begin
          writeln('measurement time elapsed');
          measuring := False;
        end;
      end;
  end;

  {$IFDEF HH400}
  HH_StopMeas(dev);
  ret := HH_GetElapsedMeasTime(dev, meastime_d);
  meastime := round(meastime_d);
  {$ENDIF}
  {$IFDEF PH300}
  PH_StopMeas(dev);
  meastime := PH_GetElapsedMeasTime(dev);
  {$ENDIF}

  writeln;
  if loop_order = repeat_sweeps then
    writeln('repetitions completed: ', repetition_index, '/', repetitions, ' (',sweeps,' sweep(s))')
  else
    writeln('sweeps completed: ', sweep_index, '/', sweeps, '(',repetitions,' repetition(s))');
  writeln;
  writeln('marker 1: ', ma1_cnt, ', marker 2: ', ma2_cnt,', marker 3: ',ma3_cnt,', marker 4: ',ma4_cnt);
  writeln('starts: ', start_cnt, ', stops: ', stop_cnt, ', syncs: ', sync_cnt, ', overflow events: ', ovl_cnt);
  writeln('detected events: ', detected_events);
  writeln;
  writeln('Measurement time: ',meastime, ' ms');
  if (meastime div 1000) > 0 then
    writeln('Average data rate: ', round((ma1_cnt + ma2_cnt + ma3_cnt + ma4_cnt + start_cnt + stop_cnt + sync_cnt + ovl_cnt) * 1000 / (meastime)), ' events/s');
  statistics[0] := start_cnt;
  statistics[1] := stop_cnt;
  statistics[2] := sync_cnt;
  statistics[3] := ma1_cnt;
  statistics[4] := ma2_cnt;
  statistics[5] := ma3_cnt;
  statistics[6] := ma4_cnt;
  statistics[7] := ovl_cnt;
  statistics[8] := meastime;
  statistics[9] := sweep_index;
  statistics[10] := repetition_index;
  statistics[11] := detected_events;
  statistics[12] := 0;
  statistics[13] := 0;
end;

{$IFDEF HH400}
initialization
  pcLibVers  := PChar(@strLibVers[0]);
  pcErrText  := PChar(@strErrText[0]);
  pcHWSerNr  := PChar(@strHWSerNr[0]);
  pcHWModel  := PChar(@strHWModel[0]);
  pcHWPartNo := PChar(@strHWPartNo[0]);
  pcWtext    := PChar(@strWtext[0]);
{$ENDIF}

end.

