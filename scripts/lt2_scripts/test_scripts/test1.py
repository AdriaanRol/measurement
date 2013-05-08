def test(string1,*args, **kw):
    print string1
    if not 'do_not_reload_AWG_seq' in args:
            print 'I am reloading the sequences'
    else:
            print 'I am not reloading the sequences'
    #if (for arg in args:arg=='kaas')
    #    print 'de eerste test'

test('peop','do_not_reload_AWG_seq')
#test('peoe1','test1')



