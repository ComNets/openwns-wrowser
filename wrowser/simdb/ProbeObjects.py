###############################################################################
# This file is part of openWNS (open Wireless Network Simulator)
# _____________________________________________________________________________
#
# Copyright (C) 2004-2007
# Chair of Communication Networks (ComNets)
# Kopernikusstr. 16, D-52074 Aachen, Germany
# phone: ++49-241-80-27910,
# fax: ++49-241-80-22242
# email: info@openwns.org
# www: http://www.openwns.org
# _____________________________________________________________________________
#
# openWNS is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 2 as published by the
# Free Software Foundation;
#
# openWNS is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import sys

import ConfigParser
configParser = ConfigParser.SafeConfigParser()
configParser.read(os.path.join(os.environ['HOME'], '.wns', 'dbAccess.conf'))
if 'Wrowser' not in configParser.sections():
    print "ERROR! Path to wrowser not in dbAccess.conf"
    exit(0)
sys.path.append(configParser.get('Wrowser', 'path'))

import wrowser.simdb.Database as db
import wrowser.Configuration as conf
import wrowser.TableParser


def getSingleResult(cls, whereClause):
    cursor = db.Database.getCursor()
    tableColumnsString = ''
    for column in cls.tableColumns:
        tableColumnsString += column + ', '
    tableColumnsString = tableColumnsString[0:-2]
    statement = 'SELECT %s FROM %s WHERE %s' % (tableColumnsString, cls.tableName, whereClause)
    #print statement
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.connection.commit()
    #print result
    if len(result) > 1:
        #raise 'To many probes match WHERE clause'
        print "Database Inconsistency after statement %s" % whereClause
        print "Taking last entry only"
        result = [ result[-1] ]
    elif len(result) == 0:
        raise 'No probe machtes WHERE clause'
    instance = cls()
    for element in xrange(len(cls.tableColumns)):
        setattr(instance, cls.tableColumns[element], result[0][element])
    return instance


def getMultipleResults(cls, whereClause):
    cursor = db.Database.getCursor()
    tableColumnsString = ''
    for column in cls.tableColumns:
        tableColumnsString += column + ', '
    tableColumnsString = tableColumnsString[0:-2]
    cursor.execute('SELECT %s FROM %s WHERE %s' % (tableColumnsString, cls.tableName, whereClause))

    result = cursor.fetchone()
    resultList = []
    while result is not None:
        instance = cls()
        for element in xrange(len(cls.tableColumns)):
            setattr(instance, cls.tableColumns[element], result[element])

        resultList.append(instance)
        result = cursor.fetchone()

    cursor.connection.commit()
    return resultList


class Moments:
    tableName = 'moments'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic']
    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "Moments"


class PDFs:
    tableName = 'pd_fs'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic',
                   'p01', 'p05', 'p50', 'p95', 'p99',
                   'min_x', 'max_x', 'number_of_bins', 'underflows', 'overflows']
    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "PDF"
    __histogram = None

    def __getHistogram(self):
        if self.__histogram == None:
            self.__histogram = getMultipleResults(PDFHistograms, "campaign_id = %d AND probe_id = %d" % (self.campaign_id, self.id))
        return self.__histogram

    histogram = property(__getHistogram)

    def __getPureHistogram(self):
        # actually there is one bin more than stated in number_of_bins
        if len(self.histogram) == self.number_of_bins + 3:
            # underflows and overflows
            return self.histogram[1:self.number_of_bins + 1]
        elif len(self.histogram) == self.number_of_bins + 2:
            # underflows or overflows
            if self.overflows > 0:
                # overflows
                return self.histogram[:self.number_of_bins + 1]
            elif self.underflows > 0:
                # underflows
                return self.histogram[1:self.number_of_bins + 2]
            else:
                raise "Did not expect to reach this line"
        else:
            # everything was fine already
            return self.histogram

    pureHistogram = property(__getPureHistogram)

class PDFHistograms:
    tableName = 'pdf_histograms'
    tableValues = ['x', 'cdf', 'ccdf', 'pdf']
    tableColumns = tableValues + ['id', 'campaign_id', 'probe_id']


class LogEvals:
    tableName = 'log_evals'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic']
    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "LogEval"

    __entries = None

    def __getEntries(self):
        if self.__entries == None:
            self.__entries = getMultipleResults(LogEvalEntries, "campaign_id = %d AND probe_id = %d" % (self.campaign_id, self.id))
        return self.__entries

    entries = property(__getEntries)


class LogEvalEntries:
    tableName = 'log_eval_entries'
    tableValues = ['x', 'y']
    tableColumns = tableValues + ['id', 'campaign_id', 'probe_id']


class BatchMeansHistograms:
    tableName = 'batch_means_histograms'
    tableValues = ['x', 'cdf', 'pdf', 'relative_error', 'confidence', 'number_of_trials_per_interval']
    tableColumns = tableValues + ['id', 'campaign_id', 'probe_id']

    def __getattr__(self, name):
        import string

        for uc in string.uppercase:
            name = name.replace(uc, "_" + uc.lower())
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError(self.__class__.__name__ + " instance has no attribute '" + name + "'")

class BatchMeans:
    tableName = 'batch_means'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic',
                   'lower_border', 'upper_border', 'number_of_intervals', 'interval_size',
                   'size_of_groups', 'maximum_relative_error', 'evaluated_groups', 'underflows',
                   'overflows', 'mean_bm', 'confidence_of_mean_absolute','confidence_of_mean_percent', 'relative_error_mean', 'variance_bm',
                   'confidence_of_variance_absolute', 'confidence_of_variance_percent','relative_error_variance', 'sigma',
                   'first_order_correlation_coefficient']
    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "BatchMeans"

    __histogram = None

    def __getHistogram(self):
        if self.__histogram == None:
            self.__histogram = getMultipleResults(BatchMeansHistograms, "campaign_id = %d AND probe_id = %d" % (self.campaign_id, self.id))
        return self.__histogram

    histogram = property(__getHistogram)


class LreHistograms:
    tableName = 'lre_histograms'
    tableValues = ['ordinate', 'abscissa', 'relative_error', 'mean_local_correlation_coefficient', 'deviation_from_mean_local_cc',
                   'number_of_trials_per_interval', 'number_of_transitions_per_interval', 'relative_error_within_limit']
    tableColumns = tableValues + ['id', 'campaign_id', 'probe_id']

    def __getattr__(self, name):
        if name == "deviationFromMeanLocalCC":
            return self.deviation_from_mean_local_cc
        import string

        for uc in string.uppercase:
            name = name.replace(uc, "_" + uc.lower())
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError(self.__class__.__name__ + " instance has no attribute '" + name + "'")

class Lres:
    tableName = 'lres'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic',
                   'lre_type', 'maximum_relative_error', 'f_max', 'f_min', 'scaling',
                   'maximum_number_of_trials_per_level', 'rho_n60', 'rho_n50',
                   'rho_n40', 'rho_n30', 'rho_n20', 'rho_n10', 'rho_00',
                   'rho_p25', 'rho_p50', 'rho_p75', 'rho_p90', 'rho_p95', 'rho_p99',
                   'peak_number_of_sorting_elements', 'level_index', 'number_of_levels',
                   'relative_error_mean', 'relative_error_variance', 'relative_error_standard_deviation',
                   'mean_local_correlation_coefficient_mean', 'mean_local_correlation_coefficient_variance',
                   'mean_local_correlation_coefficient_standard_deviation', 'number_of_trials_per_interval_mean',
                   'number_of_trials_per_interval_variance', 'number_of_trials_per_interval_standard_deviation',
                   'number_of_transitions_per_interval_mean', 'number_of_transitions_per_interval_variance',
                   'number_of_transitions_per_interval_standard_deviation']

    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "LRE"

    __histogram = None

    def __getHistogram(self):
        if self.__histogram == None:
            self.__histogram = getMultipleResults(LreHistograms, "campaign_id = %d AND probe_id = %d" % (self.campaign_id, self.id))
        return self.__histogram

    histogram = property(__getHistogram)


class DlreHistograms:
    tableName = 'lre_histograms'
    tableValues = ['ordinate', 'abscissa', 'relative_error', 'mean_local_correlation_coefficient', 'deviation_from_mean_local_cc',
                   'number_of_trials_per_interval', 'number_of_transitions_per_interval', 'relative_error_within_limit']
    tableColumns = tableValues + ['id', 'campaign_id', 'probe_id']

    def __getattr__(self, name):
        if name == "deviationFromMeanLocalCC":
            return self.deviation_from_mean_local_cc
        import string

        for uc in string.uppercase:
            name = name.replace(uc, "_" + uc.lower())
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError(self.__class__.__name__ + " instance has no attribute '" + name + "'")

class Dlres:
    tableName = 'dlres'
    tableValues = ['filename', 'name', 'alt_name', 'description', 'minimum', 'maximum', 'trials',
                   'mean', 'variance', 'relative_variance', 'standard_deviation', 'relative_standard_deviation',
                   'skewness', 'moment2', 'moment3', 'sum_of_all_values', 'sum_of_all_values_square', 'sum_of_all_values_cubic',
                   'dlre_type', 'lower_border', 'upper_border', 'number_of_intervals',
                   'interval_size', 'maximum_number_of_samples', 'maximum_relative_error_percent',
                   'evaluated_levels', 'underflows', 'overflows']

    valueNames = [name for name in tableValues if name not in ['filename', 'name', 'alt_name', 'description']]
    tableColumns = tableValues + ['id', 'campaign_id', 'scenario_id']
    probeType = "DLRE"

    __histogram = None

    def __getHistogram(self):
        if self.__histogram == None:
            self.__histogram = getMultipleResults(DlreHistograms, "campaign_id = %d AND probe_id = %d" % (self.campaign_id, self.id))
        return self.__histogram

    histogram = property(__getHistogram)


class Tables:
    fileNameSigs = ['_mean',
                    '_max',
                    '_min',
                    '_trials',
                    '_var',
                    ] # there are more than these, but these are the most commonly used ones.
    valueNames = ["minimum", "maximum"]

    tableParser = None

    probeType = "Table"

    def __init__(self, campaignId, scenarioId, probeName):
        cursor = db.Database.getCursor()
        cursor.execute("SELECT id, filename, first_col_type, first_col_description, second_col_type, "\
                       "second_col_description, description, minimum, maximum, type FROM tables "\
                       "WHERE campaign_id = %d AND scenario_id = %d AND name = \'%s\' AND type = \'%s\'" %
                       (campaignId, scenarioId, probeName.rsplit(" ", 1)[0], probeName.rsplit(" ", 1)[1]))

        result = cursor.fetchall()
        if len(result) > 1:
            raise 'To many probes match WHERE clause'
        elif len(result) == 0:
            raise 'No probe machtes WHERE clause'
        result = result[0]

        cursor.execute("SELECT first_col, second_col, value FROM table_rows "\
                       "WHERE campaign_id = %d AND probe_id = %d" % (campaignId, result[0]))
        cursor.connection.commit()
        lineValues = cursor.fetchall()
        lines = []
        for line in lineValues:
            lines.append([float(col) for col in line])


        self.tableParser = wrowser.TableParser.TableParser(result[1], result[2], result[3],
                                                                   result[4], result[5], result[6],
                                                                   result[7], result[8], lines)

        self.name                      = probeName
        self.type                      = result[9]
        self.description               = self.tableParser.getDescription()
        self.minimum                   = self.tableParser.minimum
        self.maximum                   = self.tableParser.maximum
        self.trials                    = "-"
        self.mean                      = "-"
        self.variance                  = "-"
        self.relativeVariance          = "-"
        self.standardDeviation         = "-"
        self.relativeStandardDeviation = "-"
        self.skewness                  = "-"
        self.moment2                   = "-"
        self.moment3                   = "-"
