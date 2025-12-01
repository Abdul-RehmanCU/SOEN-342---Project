# OCL Expressions for Reservation System

## 1. OCL Expression for the Method that Creates a Reservation

This OCL expression specifies the contract for the `book_trip` method in the `BookingManager` class.

```ocl
context BookingManager::book_trip(travellers : Sequence(TravellerInfo), connection : TrainConnection) : Trip

pre:
  -- At least one traveller must be provided
  travellers->notEmpty() and
  -- The connection must exist and be valid
  connection.oclIsUndefined() = false and
  -- Each traveller must have valid information
  travellers->forAll(t | 
    t.first_name.oclIsUndefined() = false and 
    t.last_name.oclIsUndefined() = false and 
    t.client_id.oclIsUndefined() = false and
    t.age >= 0 and t.age <= 120
  ) and
  -- No client can have an existing reservation for this connection
  travellers->forAll(t | 
    not self._has_existing_reservation(t.client_id, connection)
  )

post:
  -- A new Trip object was created
  result.oclIsNew() and
  -- The trip has the correct booking date (set to current time)
  result.booking_date.oclIsUndefined() = false and
  -- The trip contains exactly as many reservations as travellers
  result.reservations->size() = travellers->size() and
  -- Each reservation is linked to the correct client and connection
  result.reservations->forAll(r |
    travellers->exists(t | 
      r.client.client_id = t.client_id and
      r.connection.route_id = connection.route_id
    )
  ) and
  -- Each reservation has a ticket
  result.reservations->forAll(r | r.ticket.oclIsUndefined() = false) and
  -- The trip is stored in the system
  self.trips->includes(result)
```

---

## 2. OCL Expression for the Class that Represents a Reservation

This OCL expression specifies invariants that must hold for all Reservation objects.

context Reservation

inv HasRequiredAssociations:
  -- Every reservation must be associated with exactly one client and one connection
  self.client.oclIsUndefined() = false and
  self.connection.oclIsUndefined() = false and
  self.ticket.oclIsUndefined() = false

inv NoDuplicateBookings:
  -- No client can have multiple reservations for the same connection
  Reservation.allInstances()->select(r | 
    r <> self and
    r.client.client_id = self.client.client_id and
    r.connection.route_id = self.connection.route_id
  )->isEmpty()
```

---

## Notes

### For the Method OCL Expression:
- **Preconditions** ensure that:
  - At least one traveller is provided
  - The connection is valid
  - No duplicate reservations exist for the same client-connection pair
  
- **Postconditions** ensure that:
  - A new Trip object is created
  - The trip contains the correct number of reservations
  - Each reservation is properly linked to its client and connection
  - Each reservation has an associated ticket

### For the Class OCL Expression:
- The first invariant ensures that every reservation has the required associations (client, connection, ticket)
- The second invariant ensures that no client can have duplicate reservations for the same connection
- These constraints apply to all Reservation instances in the system


