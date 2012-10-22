{
   Measurement dll for flexible, sequence-based time-resolved data acquisition
   using the time-tagged, time-resolved measurement mode (TTTR2) of PicoQuant
   single photon counters, meant to be used in combination with qtlab class
   'PQ_measurement_generator.py'

   Several sequential measurement sections can be defined by
    - type of event to be counted:
       start, stop, sync, marker 1-4, or any combination of those
       (sync, marker4 only for HydraHarp)
    - bin size (base resolution: 1 ps (HydraHarp), 4 ps (PicoHarp))
    - offset with respect to section start (in units of bin size)
    - duration (in units of bin size)
    - measurement mode (time axis, repetition axis, sweep axis,
      or any combination of those)
    - threshold (minimal valid value, maximal valid value) per section
    - threshold mode (use minimum, maximum, both or no thresholds)
    - reset event (event to start over data acquisition in current section):
       start, stop, sync, marker 1-4, or combination of those

   The event to start the next section:
    - start, stop, sync, marker 1-4, or any combination of those

   The event to abort the measurement:
    - start, stop, sync, marker 1-4, or any combination of those, or none

   Loop behaviour:
    - number of sequence repetitions and number of sweep values can be specified
    - sweeps can be repeated, or repetitions can be swept
    - for sequence, sweep and repetitions, a reset and an increment event can be
      specified: start, stop, sync, marker 1-4, automatic, or any combination
    - here, automatic means controlled by inner loop
      (e.g. in case of a sequence consisting of 4 sections, the fifth
      'start increment event' could automatically reset the sequence and/or
      automatically increment the next loop (i.e. increment repetition index or
      sweep index)

   For high data rates, a special, faster  measurement function without
   evaluation of thresholds is also provided.

   Both Picoharp 300 and Hydraharp 400 are supported as measurement device
   (set compile condition in pq_tttr_functions correspondingly as
   {$DEFINE HH400} or {$DEFINE PH300}; phlib.dll / hhlib.dll should be
   installed in 'c:\windows\system32\')

   Details about configuring and usage of pq_tttr.dll:
   see 'PQ_measurement_generator.py'

   Lucio Robledo (lucio.robledo@gmail.com), October 2011



   Note: PicoHarp driver has a bug, data acquisition just starts after two
         pulses are sent to channel0 (start).
}

library pq_tttr;

uses
  SysUtils, pq_tttr_functions;

exports start;                // starts data acquisition
exports set_dev;              // set device-id of measurement device
exports set_debuglevel;       // allows to output additional debug information
exports set_abort_condition;  // set condition which aborts data acquisition
exports add_section;          // adds a new measurement section
exports clear_sections;       // clears previously defined sections
exports TTTR2_universal_measurement; // start processing of data, with
                              // evaluation of threshold conditions
exports TTTR2_universal_measurement_speedmode_unconditional; // start processing
                              // of data, without evaluation of threshold
                              // conditions

begin
end.

