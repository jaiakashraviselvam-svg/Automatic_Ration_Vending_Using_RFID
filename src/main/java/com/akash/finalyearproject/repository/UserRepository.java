package com.akash.finalyearproject.repository;

import com.akash.finalyearproject.enitity.User;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByRfidCard(String rfidCard);
}
