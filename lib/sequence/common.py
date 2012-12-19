"""
Module contains sequence snippets and elements of general relevance
All methods return the name of the last pulse of the generated part.
"""

def phsync_element(sequence, element_name = 'phsync', **kw):
    
    sequence.add_element(element_name)
    
    sequence.add_pulse('PH_sync1', 'PH_start', element_name, duration=50)
    
    sequence.add_pulse('PH_sync2', 'PH_start', element_name, start=500, 
            duration=50, start_reference='PH_sync1', link_start_to='end')
    
    sequence.add_pulse('PH_sync_wait', 'PH_start', element_name, start = 500, 
            duration = 50, start_reference = 'PH_sync2', 
            link_start_to = 'end', amplitude = 0)

    return 'PH_sync_wait'

def green_init_element(sequence, element_name='init', **kw):

    duration = kw.pop('duration', 10000)
    chan_green = kw.pop('chan_green', 'AOM_Green')

    sequence.add_element(element_name)
    sequence.add_pulse('green_init', chan_green, element_name,
            start=0, duration=duration)

    return 'green_init'
