;;Tool Builder v0.1 - Build any software tool with Hy-interpreted pseudocode 

;;@author Andrew Phillips  
;;@copyright 2016 Andrew Phillips <skeledrew@gmail.com>

;;Tool Builder is free software; you can redistribute it and/or
;;modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
;;License as published by the Free Software Foundation; either
;;version 3 of the License, or any later version.

;;Tool Builder is distributed in the hope that it will be useful,
;;but WITHOUT ANY WARRANTY; without even the implied warranty of
;;MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;;GNU AFFERO GENERAL PUBLIC LICENSE for more details.

;;You should have received a copy of the GNU Affero General Public
;;License along with Tool Builder.  If not, see <http://www.gnu.org/licenses/>.
(import importlib dux)

(defn load [mod]
      (try
           (.reload importlib mod)
           (catch [e Exception]
                  (.import-module importlib mod))))


;; User definitions

