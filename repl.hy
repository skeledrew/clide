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
;; TB REPL

(import [loader :as -loader] io)

(setv -dish "<=: ")    
(setv -food "error... :(")     
(setv -diet "diet.hy")  
(setv -nutri "nutri")   
    
(defn eat []  ; BUG: input not registered  
      (setv -food     
            (input -dish)))     
   
(defn digest [food]    
      (do (with [[f (open -diet "a")]]    
                (.write f (+ food "
")))  
          (if (= ":=>" (slice food 0 3))   
              (swallow (slice food 4))    
              (cook food))))    
       
(defn feed []  
      (do (while True (setv -food (input -dish)) ;(eat)     
   (if (= -food "sleep-pills") (break))    
   (digest -food))))   
     
(defn swallow [food]   
;      (with [[f (open nutri "w")]]     
;            (.write f food))    
;      (.load -loader -nutri))   
       (eval (apply read [] {"from_file" (.StringIO io food)})))     
         
(defn cook [food] (cond [(= (slice food 0 3) "ex ") (print food)] [True (print "I cannot cook this food...")])) 
         
(defn prep [] (for [ingr (.split (. self food) " ")] (yield ingr)))    
    
;(defclass Ingreds []   
;          [pos 0]    
;          [[add (fn [self food] (setv (. self itms) (.split food " ")))]     
;          [next (fn [self] (setv (. self pos) (inc (. self pos))))]   
;          [get (fn [self] (get (. self itms) (. self pos)))]]) 
