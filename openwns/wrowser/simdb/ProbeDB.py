#! /usr/bin/env python
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

import openwns.wrowser.Configuration as conf
import openwns.wrowser.simdb.Database as db
import openwns.wrowser.Probe

__config = conf.Configuration()
__config.read('.campaign.conf')


def __writeMomentsProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all Moments probes in: " + dirname
    for momProbe in openwns.wrowser.Probe.MomentsProbe.readProbes(dirname).itervalues():
        if ( momProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + momProbe.name
        cursor.execute('INSERT INTO moments (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials,'\
                       ' mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3,'\
                       ' sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic)'\
                       ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, momProbe.filename, momProbe.name, momProbe.altName, momProbe.description,
                        momProbe.minimum, momProbe.maximum, momProbe.trials, momProbe.mean, momProbe.variance, momProbe.relativeVariance,
                        momProbe.standardDeviation, momProbe.relativeStandardDeviation, momProbe.skewness, momProbe.moment2, momProbe.moment3,
                        momProbe.sumOfAllValues, momProbe.sumOfAllValuesSquare, momProbe.sumOfAllValuesCubic))
    cursor.connection.commit()

def __removeMomentsProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all Moments probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM moments WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()



def __writePDFProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all PDF probes in: " + dirname
    for pdfProbe in openwns.wrowser.Probe.PDFProbe.readProbes(dirname).itervalues():
        if ( pdfProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + pdfProbe.name
        cursor.execute('INSERT INTO pd_fs (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials,'\
                       ' mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3,'\
                       ' sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, p01, p05, p50, p95, p99, min_x, max_x, number_of_bins, underflows, overflows)'\
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '\
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, pdfProbe.filename, pdfProbe.name, pdfProbe.altName, pdfProbe.description,
                        pdfProbe.minimum, pdfProbe.maximum, pdfProbe.trials, pdfProbe.mean, pdfProbe.variance, pdfProbe.relativeVariance,
                        pdfProbe.standardDeviation, pdfProbe.relativeStandardDeviation, pdfProbe.skewness, pdfProbe.moment2, pdfProbe.moment3,
                        pdfProbe.sumOfAllValues, pdfProbe.sumOfAllValuesSquare, pdfProbe.sumOfAllValuesCubic, pdfProbe.P01, pdfProbe.P05, pdfProbe.P50, pdfProbe.P95, pdfProbe.P99,
                        pdfProbe.minX, pdfProbe.maxX, pdfProbe.numberOfBins, pdfProbe.underflows, pdfProbe.overflows))
        cursor.execute('SELECT currval(\'pd_fs_id_seq\')')
        pdfsId = cursor.fetchone()[0]
        for element in pdfProbe.histogram:
            cursor.execute('INSERT INTO pdf_histograms (campaign_id, probe_id, x, cdf, ccdf, pdf)'\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\')' %
                           (campaignId, pdfsId, element.x, element.cdf, element.ccdf, element.pdf))
    cursor.connection.commit()

def __removePDFProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all PDF probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM pd_fs WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def __writeLogEvalProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all LogEval probes in: " + dirname
    for logEvalProbe in openwns.wrowser.Probe.LogEvalProbe.readProbes(dirname).itervalues():
        if ( logEvalProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + logEvalProbe.name
        cursor.execute('INSERT INTO log_evals (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials,'\
                       ' mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3,'\
                       ' sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic)'\
                       ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, logEvalProbe.filename, logEvalProbe.name, logEvalProbe.altName, logEvalProbe.description,
                        logEvalProbe.minimum, logEvalProbe.maximum, logEvalProbe.trials, logEvalProbe.mean, logEvalProbe.variance, logEvalProbe.relativeVariance,
                        logEvalProbe.standardDeviation, logEvalProbe.relativeStandardDeviation, logEvalProbe.skewness, logEvalProbe.moment2, logEvalProbe.moment3,
                        logEvalProbe.sumOfAllValues, logEvalProbe.sumOfAllValuesSquare, logEvalProbe.sumOfAllValuesCubic))
        cursor.execute('SELECT currval(\'log_evals_id_seq\')')
        logEvalsId = cursor.fetchone()[0]
        for element in logEvalProbe.entries:
            cursor.execute('INSERT INTO log_eval_entries (campaign_id, probe_id, x, y)'\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\')' %
                           (campaignId, logEvalsId, element.x, element.y))
    cursor.connection.commit()

def __removeLogEvalProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all LogEval probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM log_evals WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def __writeBatchMeansProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all BatchMeans probes in: " + dirname
    for batchMeansProbe in openwns.wrowser.Probe.BatchMeansProbe.readProbes(dirname).itervalues():
        if ( batchMeansProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + batchMeansProbe.name
        cursor.execute('INSERT INTO batch_means (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials,'\
                       ' mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3, '\
                       ' sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, lower_border, upper_border, number_of_intervals, '\
                       ' interval_size, size_of_groups, maximum_relative_error, evaluated_groups, '\
                       ' underflows, overflows, mean_bm, confidence_of_mean_absolute, confidence_of_mean_percent, relative_error_mean, variance_bm, '\
                       ' confidence_of_variance_absolute, confidence_of_variance_percent, relative_error_variance, sigma, first_order_correlation_coefficient)'\
                       ' VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'\
                       ' %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, batchMeansProbe.filename, batchMeansProbe.name, batchMeansProbe.altName, batchMeansProbe.description,
                        batchMeansProbe.minimum, batchMeansProbe.maximum, batchMeansProbe.trials, batchMeansProbe.mean, batchMeansProbe.variance, batchMeansProbe.relativeVariance,
                        batchMeansProbe.standardDeviation, batchMeansProbe.relativeStandardDeviation, batchMeansProbe.skewness, batchMeansProbe.moment2, batchMeansProbe.moment3,
                        batchMeansProbe.sumOfAllValues, batchMeansProbe.sumOfAllValuesSquare, batchMeansProbe.sumOfAllValuesCubic, batchMeansProbe.lowerBorder, batchMeansProbe.upperBorder,
                        batchMeansProbe.numberOfIntervals, batchMeansProbe.intervalSize, batchMeansProbe.sizeOfGroups,
                        batchMeansProbe.maximumRelativeError, batchMeansProbe.evaluatedGroups, batchMeansProbe.underflows, batchMeansProbe.overflows, batchMeansProbe.meanBm,
                        batchMeansProbe.confidenceOfMeanAbsolute, batchMeansProbe.confidenceOfMeanPercent, batchMeansProbe.relativeErrorMean, batchMeansProbe.varianceBm,
                        batchMeansProbe.confidenceOfVarianceAbsolute, batchMeansProbe.confidenceOfVariancePercent, batchMeansProbe.relativeErrorVariance, batchMeansProbe.sigma,
                        batchMeansProbe.firstOrderCorrelationCoefficient))
        cursor.execute('SELECT currval(\'batch_means_id_seq\')')
        batchMeansId = cursor.fetchone()[0]
        for element in batchMeansProbe.histogram:
            cursor.execute('INSERT INTO batch_means_histograms (campaign_id, probe_id, x, cdf, pdf, relative_error, confidence, number_of_trials_per_interval)'\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', %d)' %
                           (campaignId, batchMeansId, element.x, element.cdf, element.pdf, element.relativeError, element.confidence, element.numberOfTrialsPerInterval))
    cursor.connection.commit()

def __removeBatchMeansProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all BachMeans probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM batch_means WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def __writeLreProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all LRE probes in: " + dirname
    for lreProbe in openwns.wrowser.Probe.LreProbe.readProbes(dirname).itervalues():
        if ( lreProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + lreProbe.name
        cursor.execute('INSERT INTO lres (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials, '\
                       'mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3, '\
                       'sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, lre_type, maximum_relative_error, f_max, f_min, '\
                       'scaling, maximum_number_of_trials_per_level, rho_n60, rho_n50, rho_n40, rho_n30, rho_n20, rho_n10, rho_00, '\
                       'rho_p25, rho_p50, rho_p75, rho_p90, rho_p95, rho_p99, peak_number_of_sorting_elements, level_index, number_of_levels, relative_error_mean, '\
                       'relative_error_variance, relative_error_standard_deviation, mean_local_correlation_coefficient_mean, mean_local_correlation_coefficient_variance, '\
                       'mean_local_correlation_coefficient_standard_deviation, deviation_from_mean_local_cc_mean, deviation_from_mean_local_cc_variance, '\
                       'deviation_from_mean_local_cc_standard_deviation, number_of_trials_per_interval_mean, number_of_trials_per_interval_variance, '\
                       'number_of_trials_per_interval_standard_deviation, number_of_transitions_per_interval_mean, number_of_transitions_per_interval_variance, '\
                       'number_of_transitions_per_interval_standard_deviation) '\
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '\
                       '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '\
                       '%s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, lreProbe.filename, lreProbe.name, lreProbe.altName, lreProbe.description,
                        lreProbe.minimum, lreProbe.maximum, lreProbe.trials, lreProbe.mean, lreProbe.variance, lreProbe.relativeVariance,
                        lreProbe.standardDeviation, lreProbe.relativeStandardDeviation, lreProbe.skewness, lreProbe.moment2, lreProbe.moment3,
                        lreProbe.sumOfAllValues, lreProbe.sumOfAllValuesSquare, lreProbe.sumOfAllValuesCubic,
                        lreProbe.lreType, lreProbe.maximumRelativeError, lreProbe.fMax, lreProbe.fMin, lreProbe.scaling,
                        lreProbe.maximumNumberOfTrialsPerLevel, lreProbe.rhoN60, lreProbe.rhoN50,
                        lreProbe.rhoN40, lreProbe.rhoN30, lreProbe.rhoN20, lreProbe.rhoN10, lreProbe.rho00,
                        lreProbe.rhoP25, lreProbe.rhoP50, lreProbe.rhoP75, lreProbe.rhoP90, lreProbe.rhoP95, lreProbe.rhoP99,
                        lreProbe.peakNumberOfSortingElements, lreProbe.resultIndexOfCurrentLevel, lreProbe.numberOfLevels,
                        lreProbe.relativeErrorMean, lreProbe.relativeErrorVariance, lreProbe.relativeErrorStandardDeviation,
                        lreProbe.meanLocalCorrelationCoefficientMean, lreProbe.meanLocalCorrelationCoefficientVariance,
                        lreProbe.meanLocalCorrelationCoefficientStandardDeviation, lreProbe.deviationFromMeanLocalCCMean,
                        lreProbe.deviationFromMeanLocalCCVariance, lreProbe.deviationFromMeanLocalCCStandardDeviation,
                        lreProbe.numberOfTrialsPerIntervalMean, lreProbe.numberOfTrialsPerIntervalVariance,
                        lreProbe.numberOfTrialsPerIntervalStandardDeviation, lreProbe.numberOfTransitionsPerIntervalMean,
                        lreProbe.numberOfTransitionsPerIntervalVariance, lreProbe.numberOfTransitionsPerIntervalStandardDeviation))
        cursor.execute('SELECT currval(\'lres_id_seq\')')
        lreId = cursor.fetchone()[0]
        for element in lreProbe.histogram:
            cursor.execute('INSERT INTO lre_histograms (campaign_id, probe_id, ordinate, abscissa, relative_error, mean_local_correlation_coefficient, '\
                           'deviation_from_mean_local_cc, number_of_trials_per_interval, number_of_transitions_per_interval, relative_error_within_limit) '\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', %d, \'%.10f\', \'%s\')' %
                           (campaignId, lreId, element.ordinate, element.abscissa, element.relativeError, element.meanLocalCorrelationCoefficient, element.deviationFromMeanLocalCC,
                            element.numberOfTrialsPerInterval, element.numberOfTransitionsPerInterval, element.relativeErrorWithinLimit))
    cursor.connection.commit()

def __removeLreProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all LRE probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM lres WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def __writeDlreProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all DLRE probes in: " + dirname
    for dlreProbe in openwns.wrowser.Probe.DlreProbe.readProbes(dirname).itervalues():
        if ( dlreProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + dlreProbe.name
        cursor.execute('INSERT INTO dlres (campaign_id, scenario_id, filename, name, alt_name, description, minimum, maximum, trials, '\
                       'mean, variance, relative_variance, standard_deviation, relative_standard_deviation, skewness, moment2, moment3, '\
                       'sum_of_all_values, sum_of_all_values_square, sum_of_all_values_cubic, dlre_type, lower_border, upper_border, '\
                       'number_of_intervals, interval_size, maximum_number_of_samples, maximum_relative_error_percent, '\
                       'evaluated_levels, underflows, overflows) '\
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '\
                       '%s, %s, %s, %s, %s, %s, %s, %s, %s, '\
                       '%s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, dlreProbe.filename, dlreProbe.name, dlreProbe.altName, dlreProbe.description,
                        dlreProbe.minimum, dlreProbe.maximum, dlreProbe.trials, dlreProbe.mean, dlreProbe.variance, dlreProbe.relativeVariance,
                        dlreProbe.standardDeviation, dlreProbe.relativeStandardDeviation, dlreProbe.skewness, dlreProbe.moment2, dlreProbe.moment3,
                        dlreProbe.sumOfAllValues, dlreProbe.sumOfAllValuesSquare, dlreProbe.sumOfAllValuesCubic,
                        dlreProbe.dlreType, dlreProbe.lowerBorder, dlreProbe.upperBorder, dlreProbe.numberOfIntervals, dlreProbe.intervalSize,
                        dlreProbe.maximumNumberOfSamples, dlreProbe.maximumRelativeErrorPercent, dlreProbe.evaluatedLevels,
                        dlreProbe.underflows, dlreProbe.overflows))
        cursor.execute('SELECT currval(\'dlres_id_seq\')')
        dlreId = cursor.fetchone()[0]
        for element in dlreProbe.histogram:
            cursor.execute('INSERT INTO dlre_histograms (campaign_id, probe_id, abscissa, ordinate, relative_error, mean_local_correlation_coefficient, '\
                           'deviation_from_mean_local_cc, number_of_trials_per_interval, number_of_transitions_per_interval, relative_error_within_limit) '\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', \'%.10f\', %d, \'%.10f\', \'%s\')' %
                           (campaignId, dlreId, element.ordinate, element.abscissa, element.relativeError, element.meanLocalCorrelationCoefficient, element.deviationFromMeanLocalCC,
                            element.numberOfTrialsPerInterval, element.numberOfTransitionsPerInterval, element.relativeErrorWithinLimit))
    cursor.connection.commit()

def __removeDlreProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all DLRE probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM dlres WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def __writeTableProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor):
    print "  Reading all Table probes in: " + dirname
    for tableProbe in openwns.wrowser.Probe.TableProbe.readProbes(dirname).itervalues():
        if ( tableProbe.trials == 0 and skipNullTrials ): continue
        print "    Writing to database: " + tableProbe.name
        cursor.execute('INSERT INTO tables (campaign_id, scenario_id, filename, name, type, first_col_type, first_col_description, second_col_type, '\
                       'second_col_description, description, minimum, maximum) '\
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)' , \
                       (campaignId, scenarioId, tableProbe.filename, tableProbe.name, tableProbe.type, tableProbe.tableParser.firstRowContains,
                        tableProbe.tableParser.firstRowIdName, tableProbe.tableParser.secondRowContains, tableProbe.tableParser.secondRowIdName, tableProbe.description,
                        tableProbe.minimum, tableProbe.maximum))
        cursor.execute('SELECT currval(\'tables_id_seq\')')
        tableId = cursor.fetchone()[0]
        for element in tableProbe.tableParser.lines:
            cursor.execute('INSERT INTO table_rows (campaign_id, probe_id, first_col, second_col, value) '\
                           'VALUES (%d, %d, \'%.10f\', \'%.10f\', \'%.10f\')' %
                           (campaignId, tableId, element[0], element[1], element[-1]))
    cursor.connection.commit()

def __removeTableProbesFromDB(scenarioId, campaignId, cursor):
    print "  Removing all Table probes for scenario: " + str(scenarioId)

    statement = "DELETE FROM tables WHERE campaign_id = %d AND scenario_id = %d" % (campaignId, scenarioId)
    cursor.execute(statement)
    cursor.connection.commit()

def writeAllProbesIntoDB(dirname, scenarioId, skipNullTrials = False, config = __config):
    campaignId = config.campaignId
    db.Database.connectConf(config)
    cursor = db.Database.getCursor()
    __writeMomentsProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writePDFProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writeLogEvalProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writeBatchMeansProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writeLreProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writeDlreProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)
    __writeTableProbesIntoDB(dirname, scenarioId, skipNullTrials, campaignId, cursor)

def removeAllProbesFromDB(scenarioId, config = __config):
    campaignId = config.campaignId
    db.Database.connectConf(config)
    cursor = db.Database.getCursor()
    __removeMomentsProbesFromDB(scenarioId, campaignId, cursor)
    __removePDFProbesFromDB(scenarioId, campaignId, cursor)
    __removeLogEvalProbesFromDB(scenarioId, campaignId, cursor)
    __removeBatchMeansProbesFromDB(scenarioId, campaignId, cursor)
    __removeLreProbesFromDB(scenarioId, campaignId, cursor)
    __removeDlreProbesFromDB(scenarioId, campaignId, cursor)
    __removeTableProbesFromDB(scenarioId, campaignId, cursor)

def writeCrashedScenariosIntoDB(dirname = os.getcwd(), config = __config):
    campaignId = config.campaignId
    db.Database.connectConf(config)
    cursor = db.Database.getCursor()
    statement = "SELECT id FROM scenarios WHERE campaign_id = %d AND state = \'Crashed\'" % campaignId
    print statement
    cursor.execute(statement)
    crashedIds = [ Id[0] for Id in cursor.fetchall() ]
    cursor.connection.commit()

    for Id in crashedIds:
        path = os.path.join(dirname, str(Id), 'output')
        print "Path=%s scenarioId=%d" % (path, Id)
        assert os.path.exists(path), "The specified output dir (%s) does not exist !!" % path
        assert not os.path.islink(path), "The output still resides in a symlinked dir on a remote machine !!"
        removeAllProbesFromDB(Id, config)
        writeAllProbesIntoDB(path, Id, config = config)
