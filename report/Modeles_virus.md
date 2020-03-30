# Modèles de propagation de virus 



Durant les dernières décennies, de nombreux modèles ont été développés en épidémiologie ainsi qu’en économie des réseaux pour étudier la propagation d’infection dans la population. Deux des modèles canoniques sont:


**Le modèle SIR** (Susceptible Infected Recovered) dans lequel un individu peut connaître trois états:

* Susceptible: l’individu n’est pas malade mais peut le devenir
* Infected: l’individu est infecté et peut contaminer des individus Susceptible
* Recovered: l’individu a guéri et est immunisé contre l’infection

**Le modèle SIS** (Susceptible Infected Susceptible) dans lequel un individu redevient Susceptible après avoir guéri de l’infection. Il n’y a donc pas d’immunisation ici.



De nombreuses variantes de ces modèles ont été développées plus tard, par exemple:

* **le MSIR**: l’état M (Maternal-derived immunity) est ajouté et prend en compte les nouveaux-nés immunisés qui deviendront ensuite Susceptibles.

* **le SEIR** (Susceptible Exposed Infected Recovered): l’état E prend en compte la période d’exposition prend en compte les personnes infectées mais qui ne sont pas encore contagieuses.

* **le SEIS** (Susceptible Exposed Infected Susceptible)


Dans le cadre de ce projet, afin d’étudier la propagation du Covid-19 dans une population donnée, nous avons choisi de **mettre en place un modèle SIR**. En effet, ce modèle apparaît plus pertinent que le modèle SIS car il est possible pour un individu de mourir comme de guérir du Covid-19 et ainsi d’être immunisé, même si la période d’immunisation n’a pas été précisément définie pour le moment.

Pour la mise en place d’un modèle SIR, on doit définir deux paramètres qui permettent de calculer la proportion de chaque groupe dans la population.  



![](SIR.png)












Le ***paramètre beta*** (β)  permet d’évaluer la contagion des individus sains en prenant en compte leur nombre ainsi que le nombre de personnes déjà affectées.   
Le ***paramètre gamma*** (γ) quant à lui permet de prendre en compte la période nécessaire à la guérison et donc l’immunisation des personnes infectées.











*Sources*:

https://towardsdatascience.com/social-distancing-to-slow-the-coronavirus-768292f04296

https://interstices.info/modeliser-la-propagation-dune-epidemie/?fbclid=IwAR06Kk8jcdav3WmdscPq1So5v_VJHgWmBHBprFDD308Y6dTQcH0hERrabcw

https://towardsdatascience.com/modelling-the-coronavirus-epidemic-spreading-in-a-city-with-python-babd14d82fa2

https://en.wikipedia.org/wiki/Compartmental_models_in_epidemiology#Elaborations_on_the_basic_SIR_model

Matthew O. Jackson. Social and Economic Networks. 2008.
