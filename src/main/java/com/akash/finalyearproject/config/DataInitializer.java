package com.akash.finalyearproject.config;

import com.akash.finalyearproject.enitity.User;
import com.akash.finalyearproject.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.util.Arrays;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Override
    public void run(String... args) throws Exception {
        if (userRepository.count() == 0) {
            List<User> users = Arrays.asList(
                User.builder().username("Akash").rfidCard("RFID001")
                    .password(passwordEncoder.encode("akash123"))
                    .phone("9876543210").address("Chennai").build(),
                User.builder().username("Priya").rfidCard("RFID002")
                    .password(passwordEncoder.encode("priya123"))
                    .phone("9876543211").address("Mumbai").build(),
                User.builder().username("Rahul").rfidCard("RFID003")
                    .password(passwordEncoder.encode("rahul123"))
                    .phone("9876543212").address("Delhi").build(),
                User.builder().username("Sneha").rfidCard("RFID004")
                    .password(passwordEncoder.encode("sneha123"))
                    .phone("9876543213").address("Bangalore").build(),
                User.builder().username("Vikram").rfidCard("RFID005")
                    .password(passwordEncoder.encode("vikram123"))
                    .phone("9876543214").address("Hyderabad").build()
            );
            userRepository.saveAll(users);
        }
    }
}
