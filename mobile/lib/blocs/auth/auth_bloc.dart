import 'dart:async';
import 'dart:convert';
import 'package:bloc/bloc.dart';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:http/http.dart' as http;
import 'package:mobile/pages/login_page.dart';

import 'package:mobile/pages/home_page.dart';
import 'auth_event.dart';
import 'auth_state.dart';

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitialState()) {
    on<LoginEvent>(_onLoginEvent);
    on<RegisterEvent>(_onRegisterEvent);
  }

  Future<void> _onLoginEvent(LoginEvent event, Emitter<AuthState> emit) async {
    emit(AuthLoadingState());
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/users/login/'),
        body: {
          'username': event.username,
          'password': event.password,
        },
      );
      if (response.statusCode == 200) {
        Navigator.pushNamedAndRemoveUntil(
          event.context,
          HomePage.routeName,
          (route) => false,
        );
        emit(AuthLoggedInState());
      } else {
        final Map<String, dynamic> responseData = jsonDecode(response.body);
        final String errorMessage = responseData['error'] ?? 'Login failed.';
        emit(AuthErrorState(errorMessage));
      }
    } catch (e) {
      emit(AuthErrorState('Error occurred while logging in.'));
    }
  }

  Future<void> _onRegisterEvent(
      RegisterEvent event, Emitter<AuthState> emit) async {
    print("Username: " + event.username);
    print("Password: " + event.password);
    emit(AuthLoadingState());
    try {
      final response = await http.post(
        Uri.parse('http://127.0.0.1:8000/api/users/register/'),
        body: {'password': event.password, 'username': event.username},
      );
      if (response.statusCode == 201) {
        ScaffoldMessenger.of(event.context).showSnackBar(
          SnackBar(
            content: Text('Registered successfully'),
            duration: Duration(seconds: 3),
          ),
        );
        Navigator.pushNamedAndRemoveUntil(
          event.context,
          LoginPage.routeName,
          (route) => false,
        );
        emit(AuthLoggedInState());
      } else {
        final Map<String, dynamic> responseData = jsonDecode(response.body);
        final String errorMessage =
            responseData['error'] ?? 'Registration failed.';
        emit(AuthErrorState(errorMessage));
      }
    } catch (e) {
      emit(AuthErrorState('Error occurred while registering.'));
    }
  }
}
