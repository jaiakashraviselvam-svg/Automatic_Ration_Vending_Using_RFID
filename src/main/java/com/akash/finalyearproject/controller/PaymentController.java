package com.akash.finalyearproject.controller;

import com.akash.finalyearproject.enitity.Order;
import com.akash.finalyearproject.service.OrderService;
import com.akash.finalyearproject.service.QrCodeService;
import jakarta.servlet.http.HttpSession;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

@Controller
public class PaymentController {

    @Autowired
    private OrderService orderService;

    @Autowired
    private QrCodeService qrCodeService;

    @GetMapping("/payment")
    public String payment(HttpSession session, Model model) {
        Long orderId = (Long) session.getAttribute("pendingOrderId");
        if (orderId == null) return "redirect:/dashboard";

        Order order = orderService.getOrder(orderId);
        if (order == null) return "redirect:/dashboard";

        String qrCode = null;
        try {
            String upiString = "upi://pay?pa=jaiakashraviselvam@oksbi&pn=RationPortal&am="
                    + order.getTotalAmount() + "&cu=INR&tn=RationOrder";
            qrCode = qrCodeService.generateQRCode(upiString);
        } catch (Exception ignored) {}

        model.addAttribute("order", order);
        model.addAttribute("qrCode", qrCode);
        return "payment";
    }

    @PostMapping("/payment/confirm")
    public String confirmPayment(HttpSession session) {
        Long orderId = (Long) session.getAttribute("pendingOrderId");
        if (orderId == null) return "redirect:/dashboard";

        orderService.confirmPayment(orderId);
        session.removeAttribute("pendingOrderId");
        session.setAttribute("paidOrderId", orderId);
        return "redirect:/payment/success";
    }

    @GetMapping("/payment/success")
    public String paymentSuccess(HttpSession session, Model model) {
        Long orderId = (Long) session.getAttribute("paidOrderId");
        if (orderId == null) return "redirect:/dashboard";

        Order order = orderService.getOrder(orderId);
        model.addAttribute("order", order);
        return "payment-success";
    }
}
