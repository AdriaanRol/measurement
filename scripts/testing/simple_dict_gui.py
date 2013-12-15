from enthought.traits.api \
    import HasTraits, Instance

from enthought.traits.ui.api \
    import View, VGroup, Item, ValueEditor, TreeEditor

class DictEditor(HasTraits):
    Object = Instance( object )

    def __init__(self, obj, **traits):
        super(DictEditor, self).__init__(**traits)
        self.Object = obj

    def trait_view(self, name=None, view_elements=None):
        return View(
          VGroup(
            Item( 'Object',
                  label      = 'Debug',
                  id         = 'debug',
                  editor     = ValueEditor(),
                  style      = 'custom',
                  dock       = 'horizontal',
                  show_label = False,
            ),
          ),
          title     = 'Dictionary Editor',
          width     = 800,
          height    = 600,
          resizable = True,
        )


def build_sample_data():
    my_data = dict(zip(range(10),range(10,20)))
    my_data[11] = dict(zip(range(10),range(10,20)))
    my_data[11][11] = dict(zip(range(10),range(10,20)))
    return my_data

# Test
if __name__ == '__main__':
    my_data = qt.cfgman['protocols']['AdwinSSRO']
    b = DictEditor(my_data)
    b.configure_traits()