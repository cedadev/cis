from setuptools.command.test import test as TestCommand
import multiprocessing

class nose_test(TestCommand):
    """
    Command to run unit tests
    """
    description = "Run CIS tests. By default this will run all of the unit tests. Optionally the integration tests can" \
                  " be run instead."
    user_options = [('integration-tests', 'i', 'Run the integration tests.'),
                    ('stop', 'x', 'Stop running tests after the first error or failure.'),
                    ('num-processors=', 'p', 'The number of processors used for running the tests.')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.integration_tests = False
        self.stop = False
        self.num_processors = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
        if self.integration_tests:
            self.test_set = 'jasmin_cis.test.integration'
        else:
            self.test_set = 'jasmin_cis.test.unit'

        if self.num_processors is None:
            self.num_processors = multiprocessing.cpu_count() - 1
        else:
            self.num_processors = int(self.num_processors)

    def run_tests(self):
        import nose

        n_processors = max(self.num_processors, 1)

        args = ['', self.test_set, '--processes=%s' % n_processors, '--verbosity=2',]

        if self.stop:
            args.append('--stop')

        nose.run(argv=args)

        # nose.run_exit(argv=['nosetests',os.path.join(os.path.dirname(__file__), 'unit')])

