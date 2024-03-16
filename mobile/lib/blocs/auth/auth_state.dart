import 'package:equatable/equatable.dart';

abstract class AuthState extends Equatable {
  const AuthState();

  @override
  List<Object> get props => [];
}

class AuthInitialState extends AuthState {}

class AuthLoggedInState extends AuthState {}

class AuthErrorState extends AuthState {
  final String errorMessage;

  AuthErrorState(this.errorMessage);

  @override
  List<Object> get props => [errorMessage];
}

class AuthLoadingState extends AuthState {}
