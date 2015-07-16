from matplotlib.ticker import LogFormatter, is_close_to_int, nearest_long
from matplotlib import rcParams
import math


class LogFormatterMathtextSpecial(LogFormatter):
    """
    Special formatter for color log axis, using notation such as 2.3 x 10 ^ 4.
    This is a modified version of LogFormatterMathtext supplied by matplotlib.
    """

    def __call__(self, x, pos=None):
        """Return the format for tick val *x* at position *pos*"""
        b = self._base
        usetex = rcParams['text.usetex']

        # only label the decades
        if x == 0:
            if usetex:
                return '$0$'
            else:
                return '$\mathdefault{0}$'

        fx = math.log(abs(x)) / math.log(b)
        is_decade = is_close_to_int(fx)
        fx = math.floor(fx)

        decimal_part = x / (b**fx)

        sign_string = '-' if x < 0 else ''

        # use string formatting of the base if it is not an integer
        if b % 1 == 0.0:
            base = '%d' % b
        else:
            base = '%s' % b

        if not is_decade and self.labelOnlyBase:
            return ''
        elif not is_decade:
            if usetex:
                return '$%s\\times%s%s^{%d}$' % ('%1.1f' % decimal_part, sign_string, base, fx)
            else:
                return '$\mathdefault{%s\\times%s%s^{%d}}$' % ('%1.1f' % decimal_part, sign_string, base, fx)
        else:
            if usetex:
                return r'$%s%s^{%d}$' % (sign_string, base, nearest_long(fx))
            else:
                return r'$\mathdefault{%s%s^{%d}}$' % (sign_string, base, nearest_long(fx))
