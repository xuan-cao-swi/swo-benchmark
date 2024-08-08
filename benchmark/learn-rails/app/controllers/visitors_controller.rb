class VisitorsController < ApplicationController


  def index
    # SolarWindsOTelAPM.set_transaction_name(custom_name: 'abcdf')
    # OpenTelemetry.tracer_provider.tracer.in_span('tracer_in_span') do 
    #   SolarWindsOTelAPM.set_transaction_name(custom_name: 'abcdf')
    # end
    render :index
  end

  def new
    @visitor = Visitor.new
  end

  def create
    @visitor = Visitor.new(secure_params)
    if @visitor.valid?
      @visitor.subscribe
      flash[:notice] = "Signed up #{@visitor.email}."
      redirect_to root_path
    else
      render :new
    end
  end

  private

  def secure_params
    params.require(:visitor).permit(:email)
  end

end
