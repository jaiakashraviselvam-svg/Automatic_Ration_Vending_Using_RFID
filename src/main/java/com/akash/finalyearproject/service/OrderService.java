package com.akash.finalyearproject.service;

import com.akash.finalyearproject.enitity.Order;
import com.akash.finalyearproject.enitity.User;
import com.akash.finalyearproject.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    public Order createOrder(User user, int riceKg, int wheatKg, int sugarKg) {
        int total = (riceKg * 3) + (wheatKg * 5) + (sugarKg * 10);
        Order order = Order.builder()
                .user(user)
                .riceKg(riceKg)
                .wheatKg(wheatKg)
                .sugarKg(sugarKg)
                .totalAmount(total)
                .status("PENDING")
                .riceDispensed(false)
                .wheatDispensed(false)
                .sugarDispensed(false)
                .build();
        return orderRepository.save(order);
    }

    public Order getOrder(Long id) {
        return orderRepository.findById(id).orElse(null);
    }

    public Order getPaidOrder(User user) {
        return orderRepository.findByUserAndStatus(user, "PAID").orElse(null);
    }

    public void confirmPayment(Long orderId) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        order.setStatus("PAID");
        orderRepository.save(order);
    }

    public void dispenseItem(Long orderId, String item) {
        Order order = orderRepository.findById(orderId).orElseThrow();
        switch (item.toLowerCase()) {
            case "rice"  -> order.setRiceDispensed(true);
            case "wheat" -> order.setWheatDispensed(true);
            case "sugar" -> order.setSugarDispensed(true);
        }
        if (isFullyDispensed(order)) {
            order.setStatus("DISPENSED");
        }
        orderRepository.save(order);
    }

    public boolean isFullyDispensed(Order order) {
        boolean riceOk  = order.getRiceKg()  == 0 || order.isRiceDispensed();
        boolean wheatOk = order.getWheatKg() == 0 || order.isWheatDispensed();
        boolean sugarOk = order.getSugarKg() == 0 || order.isSugarDispensed();
        return riceOk && wheatOk && sugarOk;
    }
}
