package com.akash.finalyearproject.repository;

import com.akash.finalyearproject.enitity.Order;
import com.akash.finalyearproject.enitity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface OrderRepository extends JpaRepository<Order, Long> {
    Optional<Order> findByUserAndStatus(User user, String status);
}
