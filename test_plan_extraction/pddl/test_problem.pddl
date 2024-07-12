(define (problem test )
 	 	(:domain test )

 	 	(:objects
 	 	 	bowl - vessel
 	 	 	table - array
 	 	 	fridge - refrigerator
 	 	 	box - container
 	 	 	milk - dairy_product
 	 	 	cupboard - storage_space
 	 	 	cereal - grass
 	 	)

 	 	(:init 
 	 	
 	 	 	(isInit)
 	 	)
 	 	(:goal
 	 	 	(and 
 	 	 	 	(takeContainer-executed box)
 	 	 	 	(takeDairy_product-executed milk)
 	 	 	 	(takeVesselFromStorage_space-executed bowl cupboard)
 	 	 	 	(putVesselOnArray-executed bowl table)
 	 	 	 	(pourGrassIntoVessel-executed cereal bowl)
 	 	 	 	(pourDairy_productIntoVessel-executed milk bowl)
 	 	 	)
 	 	)
)(define (problem test )
 	 	(:domain test )

 	 	(:objects
 	 	 	cupboard - storage_space
 	 	 	fridge - refrigerator
 	 	 	milk - dairy_product
 	 	 	table - array
 	 	 	box - container
 	 	 	cereal - grass
 	 	 	bowl - vessel
 	 	)

 	 	(:init 
 	 	
 	 	 	(isInit)
 	 	)
 	 	(:goal
 	 	 	(and 
 	 	 	 	(takeContainer-executed box)
 	 	 	 	(takeDairy_product-executed milk)
 	 	 	 	(takeVesselFromStorage_space-executed bowl cupboard)
 	 	 	 	(putVesselOnArray-executed bowl table)
 	 	 	 	(pourGrassIntoVessel-executed cereal bowl)
 	 	 	 	(pourDairy_productIntoVessel-executed milk bowl)
 	 	 	)
 	 	)
)