(define (domain test )
 
 	 	( :requirements
 	 	 :strips
 	 	 :negative-preconditions
 	 	 :equality
 	 	 :typing
 	 	 :adl
 	 	)
 	 	
 	 	(:types
 	 	 	array
 	 	 	storage_space
 	 	 	vessel
 	 	 	dairy_product
 	 	 	refrigerator
 	 	 	grass
 	 	 	container
 	 	)
 	 	
 	 	(:predicates
 	 	 	(isInit)
 	 	 	(putVesselOnArray-executed ?o - vessel ?p - array)
 	 	 	(takeDairy_product-executed ?o - dairy_product)
 	 	 	(takeVesselFromStorage_space-executed ?o - vessel ?p - storage_space)
 	 	 	(takeContainer-executed ?o - container)
 	 	 	(pourDairy_productIntoVessel-executed ?o - dairy_product ?p - vessel)
 	 	 	(pourGrassIntoVessel-executed ?o - grass ?p - vessel)
 	 	)
 	 	
 	 	(:action takeContainer
 	 	 	:parameters ( ?container - container )
 	 	 	:precondition (and
 	 	 	 	(putVesselOnArray-executed bowl table))
 	 	 	:effect (and
 	 	 	 	(takeContainer-executed ?container )
 	 	 	 	)
 	 	)

 	 	(:action takeDairy_product
 	 	 	:parameters ( ?dairy_product - dairy_product )
 	 	 	:precondition (and
 	 	 	 	(pourGrassIntoVessel-executed cereal bowl))
 	 	 	:effect (and
 	 	 	 	(takeDairy_product-executed ?dairy_product )
 	 	 	 	)
 	 	)

 	 	(:action takeVesselFromStorage_space
 	 	 	:parameters ( ?vessel - vessel ?storage_space - storage_space )
 	 	 	:precondition (and
 	 	 	 	)
 	 	 	:effect (and
 	 	 	 	(takeVesselFromStorage_space-executed ?vessel ?storage_space )
 	 	 	 	)
 	 	)

 	 	(:action putVesselOnArray
 	 	 	:parameters ( ?vessel - vessel ?array - array )
 	 	 	:precondition (and
 	 	 	 	(takeVesselFromStorage_space-executed bowl cupboard))
 	 	 	:effect (and
 	 	 	 	(putVesselOnArray-executed ?vessel ?array )
 	 	 	 	)
 	 	)

 	 	(:action pourGrassIntoVessel
 	 	 	:parameters ( ?grass - grass ?vessel - vessel )
 	 	 	:precondition (and
 	 	 	 	(takeContainer-executed box))
 	 	 	:effect (and
 	 	 	 	(pourGrassIntoVessel-executed ?grass ?vessel )
 	 	 	 	)
 	 	)

 	 	(:action pourDairy_productIntoVessel
 	 	 	:parameters ( ?dairy_product - dairy_product ?vessel - vessel )
 	 	 	:precondition (and
 	 	 	 	(takeDairy_product-executed milk))
 	 	 	:effect (and
 	 	 	 	(pourDairy_productIntoVessel-executed ?dairy_product ?vessel )
 	 	 	 	)
 	 	)
)(define (domain test )
 
 	 	( :requirements
 	 	 :strips
 	 	 :negative-preconditions
 	 	 :equality
 	 	 :typing
 	 	 :adl
 	 	)
 	 	
 	 	(:types
 	 	 	storage_space
 	 	 	vessel
 	 	 	array
 	 	 	container
 	 	 	refrigerator
 	 	 	grass
 	 	 	dairy_product
 	 	)
 	 	
 	 	(:predicates
 	 	 	(isInit)
 	 	 	(pourGrassIntoVessel-executed ?o - grass ?p - vessel)
 	 	 	(takeContainer-executed ?o - container)
 	 	 	(takeDairy_product-executed ?o - dairy_product)
 	 	 	(takeVesselFromStorage_space-executed ?o - vessel ?p - storage_space)
 	 	 	(putVesselOnArray-executed ?o - vessel ?p - array)
 	 	 	(pourDairy_productIntoVessel-executed ?o - dairy_product ?p - vessel)
 	 	)
 	 	
 	 	(:action takeContainer
 	 	 	:parameters ( ?container - container )
 	 	 	:precondition (and
 	 	 	 	(putVesselOnArray-executed bowl table))
 	 	 	:effect (and
 	 	 	 	(takeContainer-executed ?container )
 	 	 	 	)
 	 	)

 	 	(:action takeDairy_product
 	 	 	:parameters ( ?dairy_product - dairy_product )
 	 	 	:precondition (and
 	 	 	 	(pourGrassIntoVessel-executed cereal bowl))
 	 	 	:effect (and
 	 	 	 	(takeDairy_product-executed ?dairy_product )
 	 	 	 	)
 	 	)

 	 	(:action takeVesselFromStorage_space
 	 	 	:parameters ( ?vessel - vessel ?storage_space - storage_space )
 	 	 	:precondition (and
 	 	 	 	)
 	 	 	:effect (and
 	 	 	 	(takeVesselFromStorage_space-executed ?vessel ?storage_space )
 	 	 	 	)
 	 	)

 	 	(:action putVesselOnArray
 	 	 	:parameters ( ?vessel - vessel ?array - array )
 	 	 	:precondition (and
 	 	 	 	(takeVesselFromStorage_space-executed bowl cupboard))
 	 	 	:effect (and
 	 	 	 	(putVesselOnArray-executed ?vessel ?array )
 	 	 	 	)
 	 	)

 	 	(:action pourGrassIntoVessel
 	 	 	:parameters ( ?grass - grass ?vessel - vessel )
 	 	 	:precondition (and
 	 	 	 	(takeContainer-executed box))
 	 	 	:effect (and
 	 	 	 	(pourGrassIntoVessel-executed ?grass ?vessel )
 	 	 	 	)
 	 	)

 	 	(:action pourDairy_productIntoVessel
 	 	 	:parameters ( ?dairy_product - dairy_product ?vessel - vessel )
 	 	 	:precondition (and
 	 	 	 	(takeDairy_product-executed milk))
 	 	 	:effect (and
 	 	 	 	(pourDairy_productIntoVessel-executed ?dairy_product ?vessel )
 	 	 	 	)
 	 	)
)