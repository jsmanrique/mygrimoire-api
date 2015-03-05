#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
# J. Manrique López de la Fuente <jsmanrique@bitergia.com>
#

from ConfigParser import SafeConfigParser

import datetime

from flask import Flask
from flask.ext import restful
from flask.ext.restful import reqparse

# Database access
from vizgrimoire.metrics.query_builder import SCMQuery
# Filters to apply
from vizgrimoire.metrics.metrics_filter import MetricFilters
# Let's start playing with git activity metrics
import vizgrimoire.metrics.scm_metrics as scm

app = Flask(__name__)
api = restful.Api(app)

def read_conf():
	parser = SafeConfigParser()
	conf_file = 'api.conf'
	file_conf = open(conf_file, 'r')
	parser.readfp(file_conf)
	file_conf.close()

	user = parser.get('database', 'user')
	password = parser.get('database', 'password')
	source_code_db = parser.get('database', 'source_code_db')
	identities_db = parser.get('database', 'identities_db')

	return SCMQuery(user, password, source_code_db, identities_db)

# Setting up global metrics filers based on query params
def set_filters(parser):
	"""Returns a MetricFilters object based on query params added."""
	parser.add_argument('startdate', type=str, help='Start date for data: yyyy-mm-dd format')
	parser.add_argument('enddate', type=str, help='End date for data: yyyy-mm-dd format')
	parser.add_argument('period', type=str, help='Data period: day, week or month')
	parser.add_argument('repository', type=str, help='Repository')
	parser.add_argument('author', type=str, help='Author name')
	parser.add_argument('domain', type=str, help='Domain name')

	args = parser.parse_args()

	# By defaut, API will provide data from now to one year ago
	now = datetime.datetime.now()
	if args['startdate'] != None:
		startdate = args['startdate']
	else:
		startdate = "'%s-%s-%s'" % (now.year-1, now.month, now.day)

	if args['enddate'] != None:
		enddate = args['enddate']
	else:
		enddate = "'%s-%s-%s'" % (now.year, now.month, now.day)

	if args['period'] != None:
		if args['period'] == 'day':
			period = MetricFilters.PERIOD_DAY
		elif args['period'] == 'week':
			period = MetricFilters.PERIOD_WEEK
		elif args['period'] == 'month':
			period = MetricFilters.PERIOD_MONTH
	else:
		period = MetricFilters.PERIOD_MONTH

	# Set basic filter, based on periodicity, startdate and endate for data retrieval
	filters = MetricFilters(period, startdate, enddate)

	if args['repository'] != None:
		filters.add_filter(MetricFilters.REPOSITORY, args['repository'])

	if args['author'] != None:
		filters.add_filter(MetricFilters.PEOPLE, args['author'])

	if args['domain'] != None:
		filters.add_filter(MetricFilters.DOMAIN, args['domain'])

	return filters

# Creating timeseries format {'date': date, 'value': value}
def set_timeseries(dates, values):
	""" Returns an array of {'date': yyyy-mm-dd, 'value': activity} objects """
	ts = []
	for item in range(len(dates)):
		d = datetime.datetime.fromtimestamp(int(dates[item])).strftime('%Y-%m-%d')
		i = {'date': d, 'value': values[item]}
		ts.append(i)
	return ts

class Main(restful.Resource):
	def get(self):
		return {'data': ['scm']}

class SCM(restful.Resource):
	def get(self):
		return {'data': ['activity', 'repositories', 'contributors', 'domains']}

class SCMActivity(restful.Resource):
	def get(self):
		parser = reqparse.RequestParser()
		filters = set_filters(parser)

		commits = scm.Commits(dbcon, filters)

		commits_agg = commits.get_agg()

		commits_ts = commits.get_ts()
		timeseries = set_timeseries(commits.get_ts()['unixtime'], commits.get_ts()['commits'])

		return {
			'name': 'commits',
			'count':commits_agg['commits'],
			'timeseries': timeseries
		}

class SCMRepositories(restful.Resource):
	def get(self):
		parser = reqparse.RequestParser()
		filters = set_filters(parser)

		repos = scm.Repositories(dbcon, filters)

		repos_list = repos.get_list()

		repos = self.set_repos_list(repos_list)

		return {
			'repositories': repos
		}

	def set_repos_list(self, repos_list):
		repos = []

		for item in range(len(repos_list['name'])):

			repos.append({'name': repos_list['name'][item], 'count': repos_list['total'][item]})

		return repos

class SCMRepository(restful.Resource):
	def get(self, repo):
		parser = reqparse.RequestParser()
		filters = set_filters(parser)

		filters.add_filter(MetricFilters.REPOSITORY, str(repo))

		commits = scm.Commits(dbcon, filters)
		timeseries = set_timeseries(commits.get_ts()['unixtime'], commits.get_ts()['commits'])
		contributors = scm.Authors(dbcon, filters)
		domains = scm.Domains(dbcon, filters)

		return {
			'name':repo,
			'commits': {
				'count':commits.get_agg()['commits'],
				'timeseries': timeseries
			},
			'contributors': contributors.get_list()['authors'],
			'domains': domains.get_list()['name']
		}

class SCMContributors(restful.Resource):
	def get(self):
		parser = reqparse.RequestParser()
		filters = set_filters(parser)

		contributors = scm.Authors(dbcon, filters)

		contributors_list = contributors.get_list()

		return {'contributors': contributors_list }

class SCMContributor(restful.Resource):
	def get(self, author):
		parser = reqparse.RequestParser()
		filters = set_filters(parser)

		filters.add_filter(MetricFilters.PEOPLE, str(author))

		commits = scm.Commits(dbcon, filters)
		timeseries = set_timeseries(commits.get_ts()['unixtime'], commits.get_ts()['commits'])
		repositories = scm.Repositories(dbcon, filters)
		domains = scm.Domains(dbcon, filters)

		return {
			'name':author,
			'commits': {
				'count':commits.get_agg()['commits'],
				'timeseries': timeseries
			},
			'repositories': repositories.get_list()['name'],
			'domains': domains.get_list()['name']
		}

# routers set up
api.add_resource(Main, '/')
api.add_resource(SCM, '/scm', '/scm/')
api.add_resource(SCMActivity, '/scm/actvity', '/scm/activity/')
api.add_resource(SCMRepositories, '/scm/repositories', '/scm/repositories/')
api.add_resource(SCMRepository, '/scm/repositories/<string:repo>', '/scm/repositories/<string:repo>/')
api.add_resource(SCMContributors, '/scm/contributors', '/scm/contributors/')
api.add_resource(SCMContributor, '/scm/contributors/<string:author>', '/scm/contributors/<string:author>/')

if __name__ == '__main__':
	
	dbcon = read_conf()

	app.run(debug=True)
