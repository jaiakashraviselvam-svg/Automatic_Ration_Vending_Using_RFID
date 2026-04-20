package com.akash.finalyearproject.enitity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "`user`")
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String username;

    @Column(unique = true)
    private String rfidCard;

    private String password;

    private String phone;

    private String address;
}
