package com.akash.finalyearproject.enitity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "orders")
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Getter
@Setter
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne
    @JoinColumn(name = "user_id")
    private User user;

    private int riceKg;
    private int wheatKg;
    private int sugarKg;
    private int totalAmount;

    private boolean riceDispensed;
    private boolean wheatDispensed;
    private boolean sugarDispensed;

    private String status; // PENDING, PAID, DISPENSED

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
