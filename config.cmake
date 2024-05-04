#           __        _
#  ________/ /  ___ _(_)__  ___
# / __/ __/ _ \/ _ `/ / _ \/ -_)
# \__/\__/_//_/\_,_/_/_//_/\__/
# 
# Copyright (C) Clément Chaine
# This file is part of ECAP5-TREQ <https://github.com/cchaine/ECAP5-TREQ>
# 
# ECAP5-TREQ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# ECAP5-TREQ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with ECAP5-TREQ.  If not, see <http://www.gnu.org/licenses/>.

######################################################################
#
# DESCRIPTION: CMake configuration file for ECAP5-TREQ
#
# Include it in your CMakeLists.txt using:
#
#   include(<path to this file>)
#
#
# The following variables shall be defined :
#   
#   ecap5_treq_EXECUTABLE : path to the ecap5-treq executable
#
# The following optional variables can be defined :
#   
#   ecap5_treq_CONFIG_PATH : path to the ecap5-treq configuration file
#
######################################################################

if(DEFINED ecap5_treq_EXECUTABLE)
  if(NOT DEFINED ecap5_treq_CONFIG_PATH)
    set(ecap5_treq_CONFIG_PATH ${CMAKE_SOURCE_DIR}/config/treq.json)
  endif()

  # Define commands for using ECAP5-TREQ
  add_custom_target(report
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${ecap5_treq_EXECUTABLE} -c ${ecap5_treq_CONFIG_PATH} gen_report -o ${CMAKE_BINARY_DIR}/report.html --html)
  add_custom_command(
    OUTPUT report.md
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${ecap5_treq_EXECUTABLE} -c ${ecap5_treq_CONFIG_PATH} gen_report -o ${CMAKE_BINARY_DIR}/report.md)
  add_custom_target(report_markdown DEPENDS report.md)
  add_custom_command(
    OUTPUT test-result-badge.json
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${ecap5_treq_EXECUTABLE} -c ${ecap5_treq_CONFIG_PATH} gen_test_result_badge -o ${CMAKE_BINARY_DIR}/test-result-badge.json)
  add_custom_command(
    OUTPUT traceability-result-badge.json
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${ecap5_treq_EXECUTABLE} -c ${ecap5_treq_CONFIG_PATH} gen_traceability_result_badge -o ${CMAKE_BINARY_DIR}/traceability-result-badge.json)
  add_custom_target(badges DEPENDS test-result-badge.json traceability-result-badge.json)

  add_custom_command(
    OUTPUT traceability-matrix.csv
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    COMMAND ${ecap5_treq_EXECUTABLE} -c ${ecap5_treq_CONFIG_PATH} prepare_matrix -o ${CMAKE_BINARY_DIR}/traceability-matrix.csv)
  add_custom_target(prepare_matrix DEPENDS traceability-matrix.csv)
else()
  message(WARNING "Could not find ECAP5-TREQ")
endif()
