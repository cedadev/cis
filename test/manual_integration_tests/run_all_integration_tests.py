'''import test_plot_format_options
import test_plot
import test_io.test_read

def call_all_methods_in_module(module):
    for name in dir(module):
        attribute = getattr(module, name)
        is_method = hasattr(attribute, '__call__')
        if is_method:
            does_not_require_args = False
            try:
                does_not_require_args = attribute.func_code.co_argcount == 0
            except AttributeError:
                pass
            if does_not_require_args:
                attribute()


call_all_methods_in_module(test_plot_format_options)
call_all_methods_in_module(test_plot)
call_all_methods_in_module(test_io.test_read)'''