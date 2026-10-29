from django.db import transaction
from rest_framework import serializers, exceptions
from .models import Cart, CartItem, Product, User, Order, OrderItem, Customer


class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                'No product with given product id found')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            item.quantity += quantity
            item.save()
            self.instance = item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        try:
            user = User.objects.get(email=email)  # 1ms
        except User.DoesNotExist:
            # user.check_password(wrongpassword)
            raise exceptions.ValidationError(
                "Invalid email or password."
            )

        if not user.check_password(password):  # 2ms
            raise exceptions.ValidationError(
                "Invalid email or password."
            )

        if not user.is_active:
            raise exceptions.ValidationError(
                "User account is inactive."
            )

        attrs["user"] = user
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password"]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )

        return value

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(
            email=validated_data["email"],
            # because AbstractUser requires username
            username=validated_data["email"],
            is_staff=False,
            is_superuser=False,
            is_active=True,
        )

        user.set_password(password)
        user.save()

        return user


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "quantity", "unit_price", "product"]


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "placed_at", "payment_status", "orderitems"]


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        """Validate cart id is valid and cart have items"""
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError("Cart id does not exists")
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError("Cart is empty")
        return cart_id

    def save(self, **kwargs):
        """As multiple db operations involved, kept everythin in transaction"""
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']

            """Create Order"""
            (customer, created) = Customer.objects.get_or_create(
                user_id=self.request.user.id)
            order = Order.objects.create(customer=customer)

            """Map Cart Items to Order Items"""
            cart_items = CartItem.objects.select_related('product').filter(
                cart_id=cart_id)
            order_items = [OrderItem(order=order, product=item.product, quantity=item.quantity,
                                     unit_price=item.unit_price) for item in cart_items]

            """Create Order Items"""
            OrderItem.objects.bulk_create(order_items)

            """Delete the Cart"""
            Cart.objects.filter(pk=cart_id).delete()

            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["payment_status"]
