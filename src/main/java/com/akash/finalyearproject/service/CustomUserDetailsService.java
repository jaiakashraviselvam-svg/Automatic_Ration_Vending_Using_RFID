package com.akash.finalyearproject.service;

import com.akash.finalyearproject.enitity.User;
import com.akash.finalyearproject.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.*;
import org.springframework.stereotype.Service;

import java.util.Collections;

@Service
public class CustomUserDetailsService implements UserDetailsService {

    @Autowired
    private UserRepository userRepository;

    @Override
    public UserDetails loadUserByUsername(String rfidCard) throws UsernameNotFoundException {
        User user = userRepository.findByRfidCard(rfidCard)
                .orElseThrow(() -> new UsernameNotFoundException("User not found: " + rfidCard));
        return new org.springframework.security.core.userdetails.User(
                user.getRfidCard(),
                user.getPassword(),
                Collections.emptyList()
        );
    }
}
