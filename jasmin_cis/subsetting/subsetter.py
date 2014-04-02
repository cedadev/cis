from jasmin_cis.subsetting.subset_framework import SubsetterInterface

class Subsetter(SubsetterInterface):
    def subset(self, data, constraint):
        """Subsets the supplied data using the supplied constraint.

        :param data: data to be subsetted
        :param constraint: SubsetConstraint object to be used to subset data
        :return: subsetted data
        """
        return constraint.constrain(data)
