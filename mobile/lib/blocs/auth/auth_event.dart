import 'package:equatable/equatable.dart';
import 'package:flutter/material.dart';

abstract class AuthEvent extends Equatable {
  const AuthEvent();

  @override
  List<Object> get props => [];
}

class LoginEvent extends AuthEvent {
  final String username;
  final String password;
  final BuildContext context;
  LoginEvent(this.username, this.password, this.context);

  @override
  List<Object> get props => [username, password];
}

class RegisterEvent extends AuthEvent {
  final String password;
  final String username;
  final BuildContext context;

  RegisterEvent(this.password, this.context, this.username);

  @override
  List<Object> get props => [password, username];
}
