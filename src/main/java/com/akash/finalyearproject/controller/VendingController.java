package com.akash.finalyearproject.controller;

import com.akash.finalyearproject.enitity.Order;
import com.akash.finalyearproject.enitity.User;
import com.akash.finalyearproject.repository.UserRepository;
import com.akash.finalyearproject.service.OrderService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@Controller
@RequestMapping("/vending")
public class VendingController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderService orderService;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @GetMapping("/login")
    public String vendingLogin() {
        return "vending-login";
    }

    @PostMapping("/login")
    public String vendingLoginPost(@RequestParam String rfidCard,
                                    @RequestParam String password,
                                    HttpSession session,
                                    Model model) {
        Optional<User> userOpt = userRepository.findByRfidCard(rfidCard);

        if (userOpt.isEmpty() || !passwordEncoder.matches(password, userOpt.get().getPassword())) {
            model.addAttribute("error", "Invalid RFID card or password.");
            return "vending-login";
        }

        User user = userOpt.get();
        Order paidOrder = orderService.getPaidOrder(user);

        if (paidOrder == null) {
            model.addAttribute("error",
                    "No paid order found. Please place and pay for an order on the web portal first.");
            return "vending-login";
        }

        session.setAttribute("vendingUserId", user.getId());
        session.setAttribute("vendingOrderId", paidOrder.getId());
        return "redirect:/vending/machine";
    }

    @GetMapping("/machine")
    public String vendingMachine(HttpSession session, Model model) {
        Long orderId = (Long) session.getAttribute("vendingOrderId");
        if (orderId == null) return "redirect:/vending/login";

        Order order = orderService.getOrder(orderId);
        if (order == null) return "redirect:/vending/login";

        model.addAttribute("order", order);
        return "vending-machine";
    }

    @PostMapping("/dispense/{item}")
    public String dispense(@PathVariable String item, HttpSession session) {
        Long orderId = (Long) session.getAttribute("vendingOrderId");
        if (orderId == null) return "redirect:/vending/login";

        orderService.dispenseItem(orderId, item);

        Order order = orderService.getOrder(orderId);
        if (orderService.isFullyDispensed(order)) {
            session.removeAttribute("vendingOrderId");
            session.removeAttribute("vendingUserId");
            session.setAttribute("dispensedOrderId", orderId);
            return "redirect:/vending/thankyou";
        }
        return "redirect:/vending/machine";
    }

    @GetMapping("/thankyou")
    public String thankyou(HttpSession session, Model model) {
        Long orderId = (Long) session.getAttribute("dispensedOrderId");
        if (orderId != null) {
            Order order = orderService.getOrder(orderId);
            model.addAttribute("order", order);
            session.removeAttribute("dispensedOrderId");
        }
        return "thankyou";
    }
}
