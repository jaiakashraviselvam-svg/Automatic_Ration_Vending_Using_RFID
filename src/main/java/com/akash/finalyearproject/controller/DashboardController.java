package com.akash.finalyearproject.controller;

import com.akash.finalyearproject.enitity.Order;
import com.akash.finalyearproject.enitity.User;
import com.akash.finalyearproject.repository.UserRepository;
import com.akash.finalyearproject.service.OrderService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

@Controller
public class DashboardController {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private OrderService orderService;

    @GetMapping("/dashboard")
    public String dashboard(Authentication auth, Model model) {
        User user = userRepository.findByRfidCard(auth.getName()).orElseThrow();
        model.addAttribute("user", user);
        Order paidOrder = orderService.getPaidOrder(user);
        model.addAttribute("paidOrder", paidOrder);
        return "dashboard";
    }

    @PostMapping("/order")
    public String placeOrder(@RequestParam(defaultValue = "0") int riceKg,
                              @RequestParam(defaultValue = "0") int wheatKg,
                              @RequestParam(defaultValue = "0") int sugarKg,
                              Authentication auth,
                              HttpSession session,
                              RedirectAttributes redirectAttributes) {
        User user = userRepository.findByRfidCard(auth.getName()).orElseThrow();

        if (orderService.getPaidOrder(user) != null) {
            redirectAttributes.addFlashAttribute("error",
                    "You have a paid order waiting at the vending machine. Please collect it first.");
            return "redirect:/dashboard";
        }

        if (riceKg == 0 && wheatKg == 0 && sugarKg == 0) {
            redirectAttributes.addFlashAttribute("error", "Please select at least one item.");
            return "redirect:/dashboard";
        }

        Order order = orderService.createOrder(user, riceKg, wheatKg, sugarKg);
        session.setAttribute("pendingOrderId", order.getId());
        return "redirect:/payment";
    }
}
